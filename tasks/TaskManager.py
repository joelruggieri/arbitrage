from tasks.UndoableTask import UndoableTask
from model.Operation import Operation
from utils.injecction import Module
from rofex.model.dtos import OrderResponse
from model.enumerations import OrderStatus
from pymonad.Maybe import *
from utils.utils import *
from model.Trade import Trade
import time
import concurrent.futures
from model.Instrument import InstrumentSnapshot

#TODO ver si tiene que ser un singleton
class TaskManager:

    def do_trade(self, t0_instrument: InstrumentSnapshot, t2_instrument: InstrumentSnapshot):


