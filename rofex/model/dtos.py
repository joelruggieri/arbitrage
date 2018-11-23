from collections import namedtuple

# TODO ver cuales de todos estos valores son importante
MarketData = namedtuple("MarketData", "bids offers last_price volume min_price max_price open_price depth aggregated")

# TODO ver cuales de todos estos valores son importante
NewOrderParameters = namedtuple("NewOrderParameters", "market_id symbol price order_qty type side time_in_force account "
                                                      "cancel_previous iceberg expire_date display_quantity")

NewOrderResponse = namedtuple("NewOrderResponse", "client_id proprietary")

CancelOrderParameters = namedtuple("CancelOrderParameters", "client_id proprietary")

CancelOrderResponse = namedtuple("CancelOrderResponse", "client_id proprietary")

RetrieveOrderParameters = namedtuple("RetrieveOrderParameters", "client_id proprietary")

# TODO ver cuales de todos estos valores son importante
OrderResponse = namedtuple("OrderResponse", "order_id cl_ord_id proprietary account_id instrument_id price order_qty "
                                            "ord_type side time_in_force transact_time status")
AccountId = namedtuple("AccountId", "id")

InstrumentId = namedtuple("InstrumentId", "market_id symbol")

# TODO ver cuales de todos estos valores son importante y si hace falta mapear alguno mas
AccountPosition = namedtuple("AccountPosition", "symbol buy_price buy_size sell_price sell_size")