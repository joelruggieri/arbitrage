from collections import namedtuple

# account: str
# instrument: InstrumentSnapshot
# side: str
# price_amount: float
# volume: int
Operation = namedtuple("Operation", "account instrument side price_amount volume")
