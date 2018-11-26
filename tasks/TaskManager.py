from utils.injecction import Module
from model.Instrument import InstrumentSnapshot
from model.Operation import Operation
import concurrent.futures
from model.enumerations import OrderSide
from tasks.OrderTask import OrderTask
from pymonad.Maybe import *

#TODO ver si tiene que ser un singleton
class TaskManager:

    def do_trade(self):
        maxPriceDiffRate = float(Module.configuration()["TRADING"]["MaxPriceDifferenceRate"])
        return maxPriceDiffRate

    # Creo las dos task y las ejecuto en paralelo, luego debo analizar si salio todo bien o no y i es necesario,
    # hacer rollback
    # TODO ver si las operaciones puede ser hechas en paralelo o no
    #TODO: continue --> Ver como sabes si el future termino con exception o no
    def __schedule_transaction(self, acccout: str, t0_instrument: InstrumentSnapshot, t2_instrument: InstrumentSnapshot):
        t0_best_sell_oferror = t0_instrument.get_best_sell_oferror()
        t2_best_buy_oferror = t0_instrument.get_best_buy_oferror()

        buy_price_amount = t0_best_sell_oferror.price_amount
        sell_price_amount = t2_best_buy_oferror.price_amount

        volume = t0_best_sell_oferror.volume if t0_best_sell_oferror.volume < t2_best_buy_oferror.volume else t2_best_buy_oferror.volume

        buy_operation = Operation(acccout, t0_instrument, str(OrderSide.BUY.value), buy_price_amount, volume)
        sell_operation = Operation(acccout, t0_instrument, str(OrderSide.SELL.value), sell_price_amount, volume)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            buy_operation_result = OrderTask(buy_operation).do()
            sell_operation_result = OrderTask(sell_operation).do()


