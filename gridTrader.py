from liveTrader import liveTrading
import time
import pandas as pd
import threading
import math

class gridTrader():
    def __init__(self, params, symbol='BTC/USD'):
        self.params = params
        self.lt = liveTrading(symbol=symbol, lev=25)
        self.lt.set_leverage()
        self.lt.check_rate_limit()

    def get_processed_vars(self):
        params = self.params
        params['numberOfOrders'] = int(params['maxPositionSize']/params['sizePerOrder'])
        startTime = int(time.time())

        params['endTime'] = 10000

        if params['timeframe'] != 10000:
            params['endTime'] = startTime + 60 * params['timeframe']

        self.params = params
        return params

    def getPositionSize(self):
        return self.lt.get_position()[2]

    def checkSleep(self):
        if self.params['endTime'] == 10000:
            return True
        else:
            if time.time() < self.params['endTime']:
                return True
            else:
                return False

    def getOpenOrderPriceArray(self, totalSize):
        if self.params['mode'] == 'long':
            return self.getLongOrderPriceArray(totalSize)
        elif self.params['mode'] == 'short':
            return self.getShortOrderPriceArray(totalSize)

    def getCloseOrderPriceArray(self, totalSize):
        if self.params['mode'] == 'short':
            return self.getLongOrderPriceArray(totalSize)
        elif self.params['mode'] == 'long':
            return self.getShortOrderPriceArray(totalSize)

    def getLongOrderPriceArray(self, totalSize):
        currPrice = self.lt.get_orderbook()['best_ask']
        curr_down = int(round_down(currPrice, self.params['spread']))
        numberOfOrders = int((totalSize/self.params['sizePerOrder']))
        below_points = [curr_down - (i * self.params['spread']) for i in range(numberOfOrders)]
        return below_points

    def getShortOrderPriceArray(self, totalSize):
        currPrice = self.lt.get_orderbook()['best_bid']
        curr_up = int(round_up(currPrice, self.params['spread']))
        numberOfOrders = int(totalSize/self.params['sizePerOrder'])
        above_points = [curr_up + (i * self.params['spread']) for i in range(numberOfOrders)]
        return above_points

    def setOrders(self):
        self.orders = {}
        orders = self.lt.get_all_orders()

        if 'rnd_err' not in orders:
            orders_df = pd.DataFrame(orders)
            
            if len(orders_df) > 0:
                self.orders = orders_df[['price', 'order_id']].set_index('price').T.to_dict()

            return True

        return False

    def cleanOrders(self, array):
        count = 0
        for price, order in self.orders.items():
            if int(price) not in array:
                count = count + 1
                self.remove_order(order['order_id'])

                if count % 10 == 0:
                    time.sleep(1)

    def notOrderAlreadyPlaced(self, price):
        if str(price) not in self.orders:
            return True
        else:
            return False

    def placeOrder(self, order_type, amount, price):
        self.lt.check_rate_limit()

        t = threading.Thread(target=(self.lt.limit_trade), args=(order_type, amount, price,))
        t.start()

    def remove_order(self, order_id):
        self.lt.check_rate_limit()

        t = threading.Thread(target=(self.lt.cancel_order), args=(order_id,))
        t.start()

    def marketClosePosition(self):
        pos, entry, size = self.lt.get_position()

        if pos != "NONE":
            if size > 0:
                self.lt.market_trade('buy', abs(size))
            elif size < 0:
                self.lt.market_trade('sell', abs(size))

def round_up(x, spread):
    return int(math.ceil(x / spread)) * spread

def round_down(x, spread):
    return int(math.floor(x / spread)) * spread
    