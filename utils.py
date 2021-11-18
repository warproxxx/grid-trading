from liveTrader import liveTrading
import time
import pandas as pd
import threading
import math

class gridTrader():
    def __init__(self, params):
        self.params = params
        self.lt = liveTrading(lev=25)
        self.lt.set_leverage()

    def get_processed_vars(self):
        params = self.params
        params['numberOfOrders'] = int(params['maxPositionSize']/params['sizePerOrder'])
        startTime = int(time.time())

        params['endTime'] = -1

        if params['timeframe'] != -1:
            params['endTime'] = startTime + 60 * params['timeframe']

        self.params = params
        return params

    def getPositionSize(self):
        return self.lt.get_position()[2]

    def checkSleep(self):
        if self.params['endTime'] == -1:
            return True
        else:
            if time.time() < self.params['endTime']:
                return True
            else:
                return False

    def getLongOrderPriceArray(self, totalSize):
        currPrice = self.lt.get_orderbook()['best_ask']
        curr_down = int(round_down(currPrice, self.params['divNumber']))
        numberOfOrders = int((totalSize/self.params['sizePerOrder']) + 1)
        below_points = [curr_down - (i * self.params['divNumber']) for i in range(numberOfOrders)]
        return below_points

    def getShortOrderPriceArray(self, totalSize):
        currPrice = self.lt.get_orderbook()['best_bid']
        curr_up = int(round_up(currPrice, self.params['divNumber']))
        numberOfOrders = int((totalSize/self.params['sizePerOrder']) + 1)
        above_points = [curr_up + (i * self.params['divNumber']) for i in range(numberOfOrders)]
        return above_points

    def setOrders(self):
        self.orders = {}
        orders_df = pd.DataFrame(self.lt.get_all_orders())
        
        if len(orders_df) > 0:
            self.orders = orders_df[['price', 'order_id']].set_index('price').T.to_dict()
    
    def cleanOrders(self, array):
        for price, order_id in self.orders.items():
            if price not in array:
                self.remove_order(order_id)

    def notOrderAlreadyPlaced(self, price):
        if price not in self.orders:
            return True
        else:
            return False

    def placeOrder(self, order_type, amount, price):
        t = threading.Thread(target=(self.lt.limit_trade), args=(order_type, amount, price,))
        t.start()

    def remove_order(self, order_id):
        t = threading.Thread(target=(lt.cancel_order), args=(order_id,))
        t.start()

def round_up(x, divNumber):
    return int(math.ceil(x / divNumber)) * divNumber

def round_down(x, divNumber):
    return int(math.floor(x / divNumber)) * divNumber
    