from collections import namedtuple

# side: str
# price_amount: float
# volume: int
Offeror = namedtuple("Offeror", "side price_amount volume")
