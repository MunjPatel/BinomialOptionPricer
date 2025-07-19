class OptionPricingException:
    def __init__(self, text):
        self.text = text

    def error(self):
        return self.text

class OptionDataError(OptionPricingException):
    def __init__(self, text):
        super().__init__(text)

class TickerDataError(OptionPricingException):
    def __init__(self, text):
        super().__init__(text)

class OptionPricingError(OptionPricingException):
    def __init__(self, text):
        super().__init__(text)