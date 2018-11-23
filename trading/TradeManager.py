import asyncio
from model import Portfolio, Operation

#Este lo unico
# vamos a crear una task nueva cada vez
# en que momento hacemos el chequeo de la guita disponible
class TradeManager:

    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio

    def do_trade(self, selling_operation: Operation, buying_operation: Operation):
        selling_task = SellTask(selling_operation)



