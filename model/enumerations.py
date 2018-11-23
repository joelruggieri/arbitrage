from enum import Enum


# TODO ver el enum
class OrderSide(Enum):
    SELL = "SELL"
    BUY = "BUY"


#TODO ver cuantos estados mas hay
class OrderStatus(Enum):
    NEW = "NEW"
    REJECTED = "REJECRED"

