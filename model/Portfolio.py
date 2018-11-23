from model.enumerations import OrderSide
from model.Operation import Operation
from pymonad.Maybe import Just, Nothing, Maybe
from utils.utils import *
import uuid
from readerwriterlock import rwlock


class Portfolio:

    def __init__(self, account_id: str, initial_amount: float):
        self.cash_lock = rwlock.RWLockFair()
        self.operations_lock = rwlock.RWLockFair()
        self.account_id = account_id
        self.initial_amount = initial_amount
        self.cash = initial_amount  # TODO ver si hace falta esto . y si deberia ser 0 o el monto inicial
        self.operations = {}

    def get_cash(self) -> Maybe:
        lock = self.cash_lock.gen_rlock()
        if lock.acquire():
            try:
                return Just(self.cash)
            finally:
                lock.release()
        else:
            return Nothing



    # TODO ver el tema de la moneda
    def add_new_operation(self, operation: Operation) -> Maybe:
        factor = None
        if operation.account == self.account_id:
            if (operation.side == str(OrderSide.BUY.value)) and operation.instrument.is_counted_immediately():
                factor = -1
            elif operation.side == str(OrderSide.SELL.value) and operation.instrument.is_counted_immediately():
                factor = 1

            if factor is not None:
                trade_amount = factor * operation.price_amount * operation.volume
                lock = self.cash_lock.gen_wlock()
                operations_lock = self.cash_lock.gen_wlock()
                op_id = str(uuid.uuid4())
                if lock.acquire():
                    try:
                        if (self.cash + trade_amount) > 0:
                            if operations_lock.acquire():
                                self.operations[op_id] = operation
                                operations_lock.release()
                            else:
                                return nothing_with_message("Could not acquire operations lock")
                            current_cash = self.cash
                            self.cash = current_cash + trade_amount
                            return Just(op_id)
                        else:
                            return nothing_with_message("Has no enough money to do the trade")
                    finally:
                        lock.release()
                else:
                    return nothing_with_message("Could not acquire cash lock")
            else:
                return nothing_with_message("Side " + str(operation.side) + " unknown.")
        else:
            return nothing_with_message("Account operation " + str(operation.account) + " unknown")


# TODO ver el tema de la moneda
# TODO agregar la comision
    def remove_operation(self, operation_id: str) -> Maybe:
        factor = None
        operations_lock = self.operations_lock.gen_wlock()
        if operations_lock.acquire():
            operation = self.operations[operation_id]
            try:
                del self.operations[operation_id]
            except Exception as e:
                return nothing_with_message("Operation id " + str(operation_id) + " not exists. " + str(e))
            finally:
                operations_lock.release()
        else:
            return nothing_with_message("Could not acquire operations lock")
        if operation.account == self.account_id:
            if (operation.side == str(OrderSide.BUY.value)) and operation.instrument.is_counted_immediately():
                factor = 1
            elif operation.side == str(OrderSide.SELL.value) and operation.instrument.is_counted_immediately():
                factor = -1

            if factor is not None:
                trade_amount = factor * operation.price_amount * operation.volume
                lock = self.cash_lock.gen_wlock()
                if lock.acquire():
                    current_cash = self.cash
                    self.cash = current_cash + trade_amount
                    lock.release()
                    return Just(True)
                else:
                    return nothing_with_message("Could not acquire cash lock")
            else:
                return nothing_with_message("Side " + str(operation.side) + " unknown.")
        else:
            nothing_with_message("Account operation " + str(operation.account) + " unknown")



