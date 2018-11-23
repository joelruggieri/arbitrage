from collections import namedtuple

OrderToSend = namedtuple("OrderToSend", "instrument price volume side account")
