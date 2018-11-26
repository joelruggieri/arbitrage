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

    def is_counted_immediately(self) -> bool:
        return self.symbol.endswith(str(LiquidityPeriod.CI.value))

    def is_48_hs_delayed(self) -> bool:
        return self.symbol.endswith(str(LiquidityPeriod.T2.value))

    def get_buy_offerors(self) -> list:
        return self.__buy_offrerors

    def get_sell_oferrors(self) -> list:
        return self.__sell_offerors

    def get_best_buy_oferror(self) -> Offeror:
        best = self.__buy_offrerors[0] if self.__buy_offrerors else None
        return best

    def get_best_sell_oferror(self) -> Offeror:
        best = self.__sell_offerors[0] if self.__sell_offerors else None
        return best
