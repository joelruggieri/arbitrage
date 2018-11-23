from collections import namedtuple

#TODO ver si hace falta guardar el status de la orden
Order = namedtuple("Order", "operation client_id proprietary")