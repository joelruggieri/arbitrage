from pymonad.Maybe import *
from utils.LiquidityPeriod import LiquidityPeriod
from model.Instrument import InstrumentSnapshot


def nothing_with_message(message: str) -> Nothing:
    print(message)
    return Nothing


def obtain_homologous_instrument_symbol(instrument: InstrumentSnapshot) -> Maybe:
    if instrument.is_counted_immediately():
        return Just(instrument.symbol.replace(str(LiquidityPeriod.CI.value), str(LiquidityPeriod.T2.value)))
    if instrument.is_48_hs_delayed():
        return Just(instrument.symbol.replace(str(LiquidityPeriod.T2.value), str(LiquidityPeriod.CI.value)))
    else:
        return nothing_with_message("Symbol " + instrument.symbol + " could not understood as counted immediately neither 48hs delayed")
