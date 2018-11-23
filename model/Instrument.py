from pymonad.Maybe import *
from utils.LiquidityPeriod import LiquidityPeriod
from model.Offeror import Offeror

#TODO ver moneda
#TODO continuar con el modelado
class InstrumentSnapshot:
    def __init__(self, market_id: str, symbol: str, buy_offerors: list, sell_offerors: list):
        self.market_id = market_id
        self.symbol = symbol
        self.__buy_offrerors = buy_offerors
        self.__sell_offerors = sell_offerors

    def is_counted_immediately(self):
        return self.symbol.endswith(str(LiquidityPeriod.CI.value))

    def is_48_hs_delayed(self):
        return self.symbol.endswith(str(LiquidityPeriod.T2.value))

    def get_homologous_instrument_symbol(self):
        if self.is_counted_immediately():
            return Just(self.symbol.replace(str(LiquidityPeriod.CI.value), str(LiquidityPeriod.T2.value)))
        if self.is_48_hs_delayed():
            return Just(self.symbol.replace(str(LiquidityPeriod.T2.value), str(LiquidityPeriod.CI.value)))
        else:
            print("Symbol " + self.symbol + " could not understood as counted immediately neither 48hs delayed")
            return Nothing

    def get_buy_offerors(self):
        return self.__buy_offrerors

    def get_sell_oferrors(self):
        return self.__sell_offerors
