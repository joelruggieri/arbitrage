from model.Instrument import Instrument
from model.Operation import Operation
from model.Order import Order
from model.enumerations import OrderSide
from rofex.model.dtos import *
from rofex.client.RofexClient import RofexClient
from pymemcache.client import base
from pymonad.Maybe import *
from utils.utils import *


#TODO ver si vale la pena, mapear los modelos de rofex, a un modelo interno.
#TODO ver si no hace falta tener un servicio que nos traiga la info de la cuenta entera
class RofexFacade:

    def __init__(self, config, client: RofexClient):
        self.client = client
        cache_host = config["ROFEX.AUTH"]["CacheHost"]
        cache_port = int(config["ROFEX.AUTH"]["CachePort"])
        self.cache_ttl = int(config["ROFEX.AUTH"]["CacheTTL"])
        self.cache_client = base.Client((cache_host, cache_port))
        self.common_entries = []

    def get_auth_token(self):
        auth_token = self.cache_client.get('auth_token')
        if auth_token is not None:
            return Just(auth_token.decode("utf-8"))
        else:
            return self.client.get_auth_token() >> \
                   (lambda token: Just(self.cache_client.set('auth_token', token, expire=self.cache_ttl)) >>
                    (lambda _: Just(token)))

    #TODO ver que es el depth. si es importante o no.
    #TODO ver que onda despues la respuesta del cliente
    def get_instrument_market_data(self, instrument: Instrument, depth: int):
        return self.get_auth_token() >> (lambda token: self.client.get_market_data(token, instrument.symbol, instrument.market_id, depth))

    #TODO ver si hace falta sino sacarlo y mandarle el homologo desde afuera
    def get_homologous_instrument_market_data(self, instrument: Instrument, depth: int):
        return instrument.get_homologous_instrument_symbol >> (lambda homologous_symbol: self.get_auth_token() >>
                                                               (lambda token: self.client.get_market_data(token, homologous_symbol, instrument.market_id, depth)))

    #TODO podriamos chequear que el market id del instrumento sea el de rofex
    def new_order(self, operation: Operation):
        side = {str(OrderSide.BUY.value): Just("Buy"), str(OrderSide.SELL.value): Just("Sell")}.get(operation.side,
                                                                                                    nothing_with_message("Side " + operation.side + " unknown."))
        market_id = Just(operation.instrument.market_id) if operation.instrument.market_id == "ROFX" else nothing_with_message("Market Id should be ROFX")
        params = side >> (lambda ord_side: market_id >> (lambda m_id: Just(NewOrderParameters(market_id=m_id,
                                                                                              symbol=operation.instrument.symbol,
                                                                                              price=operation.price_amount,
                                                                                              order_qty=operation.volume,
                                                                                              side=ord_side,
                                                                                              type="Limit",  # TODO ver que onda este campo
                                                                                              time_in_force="IOC",  # TODO ver que onda este campo o si tal vez tiene que ser Day
                                                                                              account=operation.account,
                                                                                              cancel_previous=None,
                                                                                              iceberg=None,
                                                                                              expire_date=None,
                                                                                              display_quantity=None))))
        return self.get_auth_token() >> (lambda token: params >> (lambda order_params: self.client.new_order(token, order_params) >>
                                                                    (lambda new_order_response: Just(Order(operation = operation,
                                                                                                           client_id=new_order_response.client_id,
                                                                                                           proprietary=new_order_response.proprietary)))))

    def cancel_order(self, client_id: str, proprietary: str):
        return self.get_auth_token() >> (lambda token: self.client.cancel_order(token, CancelOrderParameters(client_id, proprietary)))

    def get_order(self, client_id: str, proprietary: str) -> Maybe:
        return self.get_auth_token() >> (lambda token: self.client.get_order_status_with_last_status(token, RetrieveOrderParameters(client_id, proprietary)))

    def get_account_positions(self, account_name: str):
        return self.get_auth_token() >> (lambda token: self.client.get_account_positions(token, account_name))



