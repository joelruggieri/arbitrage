# coding=utf-8
import requests
from requests.sessions import *
from requests.exceptions import *
from pymonad.Maybe import *
import json as simplejson
from rofex.model.dtos import *


class RofexClient:
    def __init__(self, config):
        self.protocol = config["ROFEX"]["Protocol"]
        self.host = config["ROFEX"]["Host"]
        self.user = config["ROFEX"]["User"]
        self.password = config["ROFEX"]["Password"]
        self.common_market_data_entries = ["BI", "OF", "TV", "LO", "HI", "OP"]

    def get_auth_token(self):
        auth_session = requests.session()
        login_url = self.protocol + "://" + self.host + "/auth/getToken"
        headers = {'X-Username': self.user, 'X-Password': self.password}
        try:
            login_response = auth_session.post(login_url, headers=headers)
            print(login_response)
            if login_response.ok and "X-Auth-Token" in login_response.headers:
                print("successful login")
                return Just(login_response.headers["X-Auth-Token"])
            else:
                print("could not login: " + str(login_response))
                return Nothing
        except RequestException:
            print("could not login")
            return Nothing

    def get_market_data(self, auth_token: str, symbol: str, market_id: str, depth: int):
        path = "rest/marketdata/get?marketId={m}&symbol={s}&entries={e}&depth={d}".format(m=market_id,
                                                                                          s=symbol,
                                                                                          e=",".join(self.common_market_data_entries),
                                                                                          d=depth)
        url = self.protocol + "://" + self.host + "/" + path
        #TODO ver si no hace falta checkear el status code del servicio, o el status que viene en el body del response
        try:
            auth_session = self.__get_auth_session__(auth_token)
            response = auth_session.get(url)
            response_body = simplejson.loads(response.content.decode('utf-8'))
            market_data = response_body["marketData"]
            print(market_data)
            bids = []
            offers = []
            last_price = None
            volume = None
            min_price = None
            max_price = None
            open_price = None
            depth = None
            aggregated = None
            if "BI" in market_data:
                bids = market_data["BI"]
            if "OF" in market_data:
                offers = market_data["OF"]
            if "LA" in market_data:
                last_price = market_data["LA"]
            if "TV" in market_data:
                volume = market_data["TV"]
            if "LO" in market_data:
                min_price = market_data["LO"]
            if "HI" in market_data:
                max_price = market_data["HI"]
            if "OP" in market_data:
                open_price = market_data["OP"]
            if "depth" in response_body:
                depth = response_body["depth"]
            if "aggregated" in response_body:
                aggregated = response_body["aggregated"]

            return Just(MarketData(bids=bids, offers=offers, last_price=last_price, volume=volume, min_price=min_price, max_price=max_price, open_price=open_price, depth=depth, aggregated=aggregated))

        except Exception as e:
            print(e)
            return Nothing

    def new_order(self, auth_token: str, new_order_parameters: NewOrderParameters):
        qs = {"marketId": new_order_parameters.market_id, "symbol": new_order_parameters.symbol,
              "price": new_order_parameters.price, "orderQty": new_order_parameters.order_qty,
              "ordType": new_order_parameters.type, "side": new_order_parameters.side,
              "timeInForce": new_order_parameters.time_in_force, "account": new_order_parameters.account,
              "cancelPrevious": str(new_order_parameters.cancel_previous).lower(),
              "iceberg": str(new_order_parameters.iceberg).lower(),
              "expireDate": new_order_parameters.expire_date.strftime("%Y%m%d"),
              "displayQty": new_order_parameters.display_quantity}
        url = self.protocol + "://" + self.host + "/rest/order/newSingleOrder"
        try:
            auth_session = self.__get_auth_session__(auth_token)
            response = auth_session.get(url, params=qs)
            response_body = simplejson.loads(response.content.decode('utf-8'))
            if response.ok and "order" in response_body:
                order = response_body["order"]
                client_id = order["clientId"] if "clientId" in order else None
                proprietary = order["proprietary"] if "proprietary" in order else None
                print(order)
                return Just(NewOrderResponse(client_id, proprietary))
            else:
                print("Could not send new order: " + str(response))
                return Nothing
        except Exception as e:
            print(e)
            return Nothing

    def cancel_order(self, auth_token: str, parameters: CancelOrderParameters):
        qs = {"clOrdId": parameters.client_id, "proprietary": parameters.proprietary}
        url = self.protocol + "://" + self.host + "/rest/order/cancelById"
        try:
            auth_session = self.__get_auth_session__(auth_token)
            response = auth_session.get(url, params=qs)
            response_body = simplejson.loads(response.content.decode('utf-8'))
            if response.ok and "order" in response_body:
                order = response_body["order"]
                client_id = order["clientId"] if "clientId" in order else None
                proprietary = order["proprietary"] if "proprietary" in order else None
                print(order)
                return Just(CancelOrderResponse(client_id, proprietary))
            else:
                print("Could not cancel order with client id " + str(parameters.client_id) + ". Response: " + str(response))
                return Nothing
        except Exception as e:
            print(e)
            return Nothing

    def get_order_status_with_last_status(self, auth_token: str, parameters: RetrieveOrderParameters):
        qs = {"clOrdId": parameters.client_id, "proprietary": parameters.proprietary}
        url = self.protocol + "://" + self.host + "/rest/order/id"
        try:
            auth_session = self.__get_auth_session__(auth_token)
            response = auth_session.get(url, params=qs)
            response_body = simplejson.loads(response.content.decode('utf-8'))
            if response.ok and "order" in response_body:
                order = response_body["order"]
                order_id = order["orderId"] if "orderId" in order else None
                cl_ord_id = order["clOrdId"]
                proprietary = order["proprietary"]
                account_id = AccountId(order["accountId"]["id"])
                instrument_id = InstrumentId(order["instrumentId"]["marketId"], order["instrumentId"]["symbol"])
                price = order["price"]
                order_qty = order["orderQty"]
                ord_type = order["ordType"]
                side = order["side"]
                time_in_force = order["timeInForce"]
                transact_time = order["transactTime"]
                status = order["status"]
                print(order)
                return Just(OrderResponse(order_id=order_id, cl_ord_id=cl_ord_id, proprietary=proprietary, account_id=account_id,
                                          instrument_id=instrument_id, price=price, order_qty=order_qty, ord_type=ord_type,
                                          side=side, time_in_force=time_in_force, transact_time=transact_time, status=status))
            else:
                print("Could get order with clOrdId " + str(parameters.client_id + " and proprietary " + str(parameters.proprietary) + ". Response: " + str(response)))
                return Nothing
        except Exception as e:
            print(e)
            return Nothing

    def get_account_positions(self, auth_token: str, account_name: str):
        url = self.protocol + "://" + self.host + "/rest/risk/position/getPositions/" + account_name
        try:
            auth_session = self.__get_auth_session__(auth_token)
            response = auth_session.get(url)
            response_body = simplejson.loads(response.content.decode('utf-8'))
            if response.ok and "positions" in response_body:
                print(response_body)
                positions = list()
                for position in response_body["positions"]:
                    symbol = position["symbol"]
                    buy_price = position["buyPrice"]
                    buy_size = position["buySize"]
                    sell_price = position["sellPrice"]
                    sell_size = position["sellSize"]

                    positions.append(AccountPosition(symbol=symbol, buy_price=buy_price, buy_size=buy_size, sell_price=sell_price, sell_size=sell_size))
                return Just(positions)
            else:
                print("Could not get positions for account " + str(account_name) + ". Response: " + str(response))
                return Nothing
        except Exception as e:
            print(e)
            return Nothing

    def __get_auth_session__(self, auth_token: str):
        a_session = requests.session()
        a_session.headers["X-Auth-Token"] = auth_token
        return a_session

