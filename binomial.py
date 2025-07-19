import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from dataclasses import dataclass
from exceptions import OptionDataError, OptionPricingError, TickerDataError

# @dataclass
# class OptionChains:
#     ticker: str
    
#     def _chains(self):
#         try:
#             ticker = yf.Ticker(self.ticker)
#             expiries = ticker.options
#             if not expiries:
#                 return 'No options available for the gives ticker!'
#             call_options = [ticker.option_chain(date).calls for date in expiries]
#             put_options = [ticker.option_chain(date).puts for date in expiries]
#             return [expiries, call_options, put_options]
#         except Exception as e:
#             error = OptionDataError(text=f"Failed to retrieve options data for {self.ticker}: {e}")
#             raise error.text()

@dataclass
class OptionChains:
    ticker: str

    def _chains(self):
        try:
            ticker = yf.Ticker(self.ticker)
            expiries = ticker.options
            if not expiries:
                return 'No options available for the given ticker!'

            # Convert all expiry dates to string
            expiries = [str(exp) for exp in expiries]

            call_options = [ticker.option_chain(date).calls for date in expiries]
            put_options = [ticker.option_chain(date).puts for date in expiries]

            return [expiries, call_options, put_options]
        except Exception as e:
            error = OptionDataError(text=f"Failed to retrieve options data for {self.ticker}: {e}")
            raise error.text()

@dataclass
class OptionPricing:
    ticker: str
    expiry_date: str
    option_ticker: str
    n_steps: int
    risk_free_rate: float

    def _fair_price(self):
        try:
            options_ticker = yf.Ticker(self.option_ticker)
            options_historical_data = options_ticker.history(period="max")
            properties = options_ticker.info
            ticker_info = {i: properties.get(i) for i in ['maxAge', "strikePrice", "regularMarketPrice", "underlyingSymbol", "optionsType", "expireIsoDate"]}
            
            # Ensure required fields are present
            if not all(ticker_info.values()):
                option_error = OptionDataError(text="Some option metadata is missing.")
                raise option_error.text()
            
            ticker_prop_data = yf.Ticker(self.ticker)
            volatility_data = ticker_prop_data.history(period="1y")
            if volatility_data.empty:
                ticker_data_error = TickerDataError(text=f"Insufficient historical data for {self.ticker}.")
                raise ticker_data_error.text()
            
            annual_volatility = volatility_data['Close'].pct_change().std() * np.sqrt(252)

            expiry_date = datetime.strptime(ticker_info.get('expireIsoDate'), "%Y-%m-%dT00:00:00Z").date()
            today_date = datetime.today().date()
            n_days = (expiry_date - today_date).days - 1
            time_to_maturity = n_days / 252
            delta = time_to_maturity / self.n_steps

            up_move = np.exp(annual_volatility * np.sqrt(delta))
            down_move = 1 / up_move

            up_prob = (np.exp(self.risk_free_rate * delta) - down_move) / (up_move - down_move)
            # down_prob = 1 - up_prob

            S0 = ticker_prop_data.history(period='1d')['Close'].iloc[-1]
            K = ticker_info.get('strikePrice')
            # T = time_to_maturity
            r = self.risk_free_rate
            # sigma = annual_volatility
            N = self.n_steps
            u = up_move
            d = down_move
            p = up_prob
            dt = delta
            discount = np.exp(-r * dt)

            price_tree = np.zeros((N + 1, N + 1))
            for outer_price in range(N + 1):
                for inner_price in range(outer_price + 1):
                    price_tree[inner_price, outer_price] = S0 * (u ** outer_price) * (d ** abs(outer_price - inner_price))

            option_tree = np.zeros_like(price_tree)
            for option_price in range(N + 1):
                if ticker_info.get('optionsType').lower() == 'call':
                    option_tree[option_price, N] = max(price_tree[option_price, N] - K, 0)
                else:
                    option_tree[option_price, N] = max(K - price_tree[option_price, N], 0)

            for outer_backprop_index in range(N - 1, -1, -1):
                for inner_backprop_index in range(outer_backprop_index + 1):
                    option_tree[inner_backprop_index, outer_backprop_index] = discount * (
                        p * option_tree[inner_backprop_index + 1, outer_backprop_index + 1] +
                        (1 - p) * option_tree[inner_backprop_index, outer_backprop_index + 1]
                    )

            return option_tree

        except (KeyError, ValueError, IndexError) as e:
            option_price_error = OptionPricingError(text=f"Pricing failed due to data issues: {e}")
            raise option_price_error.text()
        except Exception as e:
            option_price_exception = OptionPricingError(text=f"An unexpected error occurred in option pricing: {e}")
            raise option_price_exception.text()