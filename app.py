# import streamlit as st
# import json
# import yfinance as yf
# from datetime import datetime
# from binomial import OptionChains, OptionPricing, OptionDataError, TickerDataError, OptionPricingError

# # Load the S&P 500 ticker dictionary
# with open('s&p500.json', 'r') as file:
#     ticker_dict = json.load(file)

# st.title("Option Pricing with Binomial Tree")

# # Step 1: Select company
# company = st.selectbox("Select a company to find its option chain:", ["-- Select Company --"] + list(ticker_dict.keys()))

# if company and company != "-- Select Company --":
#     ticker = ticker_dict[company]
#     chain_instance = OptionChains(ticker)
#     results = chain_instance._chains()

#     if isinstance(results, str):
#         st.error(results)
#     else:
#         expiries, call_options, put_options = results

#         # st.write("Expiry Dates:", expiries)
#         expiries = list(expiries)  # Add this once after unpacking from results

#         # Step 2: Select expiry (only available after company is valid)
#         expiry = st.selectbox("Select an expiry date:", ["-- Select Expiry --"] + list(map(str, expiries)))

#         if expiry and expiry != "-- Select Expiry --":
#             # Step 3: Select option type (call or put)
#             option_type = st.radio("Select option type:", ('Call', 'Put'))

#             if option_type:
#                 # Step 4: Select specific option from chain
#                 options_df = call_options[expiries.index(expiry)] if option_type == 'Call' else put_options[expiries.index(expiry)]
                
#                 if options_df.empty:
#                     st.warning(f"No {option_type.lower()} options found for this expiry.")
#                 else:
#                     formatted_options = options_df.apply(lambda row: f"Strike: {row['strike']} | Last Price: {row['lastPrice']} | Bid: {row['bid']} | Ask: {row['ask']} | Symbol: {row['contractSymbol']}", axis=1)
#                     option_selected = st.selectbox("Select a specific option:", ["-- Select Option --"] + list(formatted_options))

#                     if option_selected and option_selected != "-- Select Option --":
#                         # Step 5: Evaluation input
#                         with st.form("eval_form"):
#                             st.write("### Set Parameters for Pricing")
#                             n_steps = st.number_input("Number of steps in binomial tree:", min_value=1, max_value=500, value=100)
#                             risk_free_rate = st.number_input("Risk-free rate (annual, change as per requirement):", value=0.05, step=0.01)
#                             submitted = st.form_submit_button("Evaluate Option")

#                         if submitted:
#                             contract_symbol = option_selected.split("Symbol: ")[-1]

#                             try:
#                                 pricing_instance = OptionPricing(
#                                     ticker=ticker,
#                                     expiry_date=str(expiry),
#                                     option_ticker=contract_symbol,
#                                     n_steps=n_steps,
#                                     risk_free_rate=risk_free_rate
#                                 )
#                                 option_tree = pricing_instance._fair_price()

#                                 # Extract fair value (theoretical price)
#                                 fair_value = option_tree[0][0]

#                                 # Extract market value (lastPrice)
#                                 selected_row = options_df[options_df['contractSymbol'] == contract_symbol].iloc[0]
#                                 market_value = selected_row['lastPrice']

#                                 # Comparison logic
#                                 if market_value > fair_value:
#                                     valuation_status = f"🔴 **Overvalued** by ${round(market_value - fair_value, 2)}"
#                                 elif market_value < fair_value:
#                                     valuation_status = f"🟢 **Undervalued** by ${round(fair_value - market_value, 2)}"
#                                 else:
#                                     valuation_status = "⚪ **Fairly Priced**"

#                                 # Display Results
#                                 st.markdown(f"### Binomial Option Price Tree for `{contract_symbol}`")
#                                 st.dataframe(option_tree)

#                                 st.markdown(f"""
#                                 #### Market vs Theoretical Price Comparison
#                                 - **Market Price:** ${market_value:.2f}
#                                 - **Theoretical Price (Binomial):** ${fair_value:.2f}
#                                 - **Conclusion:** {valuation_status}
#                                 """)

#                             except Exception as e:
#                                 st.error(f"Error during pricing: {e}")

import streamlit as st
import json
import yfinance as yf
from datetime import datetime
from binomial import OptionChains, OptionPricing, OptionDataError, TickerDataError, OptionPricingError

# Load S&P 500 ticker dictionary
with open('sp500.json', 'r') as file:
    ticker_dict = json.load(file)

# Title
st.markdown("<h1 style='text-align: center; color: #1E88E5;'>Binomial Option Pricing Tool</h1>", unsafe_allow_html=True)
st.markdown("Use this tool to compute the fair value of an option using the binomial tree method and compare it with market price.")

# Step 1: Select Company
company = st.selectbox("📊 Select a company:", ["-- Select Company --"] + list(ticker_dict.keys()))

if company and company != "-- Select Company --":
    ticker = ticker_dict[company]
    chain_instance = OptionChains(ticker)
    results = chain_instance._chains()

    if isinstance(results, str):
        st.error(results)
    else:
        expiries, call_options, put_options = results
        expiries = list(expiries)

        # Step 2: Select Expiry Date
        expiry = st.selectbox("📅 Select an expiry date:", ["-- Select Expiry --"] + list(map(str, expiries)))

        if expiry and expiry != "-- Select Expiry --":
            # Step 3: Select Option Type
            option_type = st.radio("📈 Select option type:", ('Call', 'Put'))

            if option_type:
                # Step 4: Select Specific Option
                options_df = call_options[expiries.index(expiry)] if option_type == 'Call' else put_options[expiries.index(expiry)]

                if options_df.empty:
                    st.warning(f"No {option_type.lower()} options found for this expiry.")
                else:
                    formatted_options = options_df.apply(
                        lambda row: f"Strike: {row['strike']} | Last Price: {row['lastPrice']} | Bid: {row['bid']} | Ask: {row['ask']} | Symbol: {row['contractSymbol']}",
                        axis=1
                    )
                    option_selected = st.selectbox("🧮 Select a specific option:", ["-- Select Option --"] + list(formatted_options))

                    if option_selected and option_selected != "-- Select Option --":
                        # Step 5: Pricing Form
                        with st.form("eval_form"):
                            st.markdown("### 🔧 Pricing Parameters")
                            col1, col2 = st.columns(2)

                            with col1:
                                n_steps = st.number_input("Number of steps in binomial tree:", min_value=1, max_value=500, value=100)

                            with col2:
                                risk_free_rate = st.number_input("Risk-free rate (e.g. 0.05 = 5%):", value=0.05, step=0.01)

                            submitted = st.form_submit_button("🚀 Evaluate Option")

                        if submitted:
                            contract_symbol = option_selected.split("Symbol: ")[-1]

                            try:
                                pricing_instance = OptionPricing(
                                    ticker=ticker,
                                    expiry_date=str(expiry),
                                    option_ticker=contract_symbol,
                                    n_steps=n_steps,
                                    risk_free_rate=risk_free_rate
                                )
                                option_tree = pricing_instance._fair_price()

                                # Theoretical value
                                fair_value = option_tree[0][0]

                                # Market value
                                selected_row = options_df[options_df['contractSymbol'] == contract_symbol].iloc[0]
                                market_value = selected_row['lastPrice']

                                # Comparison
                                if market_value > fair_value:
                                    valuation_status = f"🔴 **Overvalued** by ${round(market_value - fair_value, 2)}"
                                elif market_value < fair_value:
                                    valuation_status = f"🟢 **Undervalued** by ${round(fair_value - market_value, 2)}"
                                else:
                                    valuation_status = "⚪ **Fairly Priced**"

                                st.markdown(f"""
                                <div style="background-color:#1c1c1e; padding: 1.5rem; border-radius: 10px; border: 1px solid #333;">
                                    <h3 style="color:#f1f1f1;">📄 Pricing Summary for 
                                        <code style="font-size: 1.1rem; color:#00FFB3;">{contract_symbol}</code>
                                    </h3>
                                    <p style="font-size: 1.1rem; margin: 0.5rem 0;">
                                        <strong style="color:#f1f1f1;">Market Price:</strong> <span style="color:#FFB347;">${market_value:.2f}</span><br>
                                        <strong style="color:#f1f1f1;">Theoretical Price (Binomial):</strong> <span style="color:#7FFFD4;">${fair_value:.2f}</span><br>
                                        <strong style="color:#f1f1f1;">Conclusion:</strong> <span style="font-weight:bold; color:{'green' if market_value < fair_value else 'red'};">
                                            {'🟢 Undervalued' if market_value < fair_value else '🔴 Overvalued'} by ${abs(fair_value - market_value):.2f}
                                        </span>
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)


                                st.markdown("---")
                                # st.markdown(f"### 📉 Binomial Option Price Tree for `{contract_symbol}`")
                                st.markdown(f"""
                                <h3 style="color:#f1f1f1;">📉 Binomial Option Price Tree for <code style="color:#00FFB3;">{contract_symbol}</code></h3>
                                """, unsafe_allow_html=True)
                                st.dataframe(option_tree)

                            except Exception as e:
                                st.error(f"❌ Error during pricing: {e}")
