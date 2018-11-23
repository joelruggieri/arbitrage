from tasks.UndoableTask import UndoableTask
from model.Operation import Operation
from utils.injecction import Module
from rofex.model.dtos import OrderResponse
from model.enumerations import OrderStatus
from pymonad.Maybe import *
from utils.utils import *


# TODO Por ahora vamos a suponer que ante cualquier orden ingresa que el estado no sea NEW, es fallida, luego preguntar
# TODO bien los estados posibles que puede estar
# TODO ver si deberiamos guardar en el protfolio todas las ordenes, o solo las OK
# TODO hacer el cambio para poder trabajar con una lista de portfolios
# TODO ver logica de reintentos (mas critico para la cancelacion)
class OrderTask(UndoableTask):

    def __init__(self, operation: Operation):
        self.operation = operation
        self.portfolio = Module.portfolio()
        self.rofex_facade = Module.rofex_facade()
        self.order = None
        self.operation_id = None

    def __check_if_order_is_ok(self, order_response: OrderResponse) -> Maybe:
        if order_response.status == str(OrderStatus.NEW.value):
            Just(order_response)
        else:
            return nothing_with_message(
                "Order with order id " + str(order_response.order_id) + " and proprietary " + str(
                    order_response.proprietary) + " has not been successful. Status: " + str(order_response.status))

    def __set_operation_id(self, operation_id: str) -> Maybe:
        self.operation_id = operation_id
        return Just(True)

    def __set_order(self, order: OrderResponse) -> Maybe:
        self.order = order
        return Just(True)

    def do(self) -> Maybe:
        return self.portfolio.add_new_operation(self.operation) >> \
               (lambda op_id: self.__set_operation_id(op_id) >>
                (lambda a: self.rofex_facade.new_order(self.operation) >>
                 (lambda new_order_response: self.rofex_facade.get_order(new_order_response.client_id,
                                                                                                 new_order_response.proprietary) >>
                  (lambda order_done: self.__set_order(order_done) >>
                   (lambda b: self.__check_if_order_is_ok(order_done))))))

    # TODO mañana: si hay op_id hay que removerla del portfolio
    # si hay order hay que llamar a cancelarla (aca hay que ver como responde rofex si queres cancelar una orden que no salio con estado new)
    # TODO ver si realmente quiero eliminar la operaicion, y en ese caso, si lo quiero hacer siemre (orden no OK o error de rofex por ejemplo), o solo si falló rofex
    # TODO aa tal vez en caso de que exista orden, ver si deberiamos chequear por el estado
    def undo(self) -> Maybe:
        cancel_order_result_first_attempt = self.rofex_facade.cancel_order(self.order.cl_ord_id,
                                                                           self.order.proprietary) if self.order is not None else Just(True)

        removing_operation_result = self.portfolio.remove_operation(self.operation_id) if self.operation_id is not None \
            else Just(True) if self.order is None else \
            nothing_with_message("Unexpected result: Order exists with client id " + str(self.order.cl_ord_id) +
                                 " and proprietary " + str(self.order.proprietary) + " but operation does not exist.")

        # reintento
        # TODO tal vez habria que ver ante qué nothing hay que reintentar (tal vez ante un timeout de rofex o un internal server error)
        cancel_order_result_second_attempt_if_necessary = self.rofex_facade.cancel_order(self.order.cl_ord_id,
                                                                                         self.order.proprietary) if cancel_order_result_first_attempt is Nothing else Just(True)

        return cancel_order_result_second_attempt_if_necessary >> removing_operation_result
