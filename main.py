import argparse
from gridTrader import gridTrader
import time
import sys

parser = argparse.ArgumentParser("script.py")
    
parser.add_argument("--maxPositionSize", help="Max Position Size", type=int, default=50)
parser.add_argument("--sizePerOrder", help="Size per order", type=int, default=1)
parser.add_argument("--timeframe", help="Run time in miniutes", type=int, default=10000)
parser.add_argument("--sleepTime", help="Seconds delayed", type=int, default=15)
parser.add_argument("--divNumber", help="Divisible Price points to check at", type=int, default=10)
parser.add_argument("--mode", help="long or short", type=str, default="short")

gt = gridTrader(vars(parser.parse_args()))
params = gt.get_processed_vars()
helper = {'long': {'open': 'buy', 'close': 'sell'}, 'short': {'open': 'sell', 'close': 'buy'}}

if params['mode'] not in ['long', 'short']:
    print("Mode should be either long or short")
    sys.exit()

def perform_once():
    count = 0
    openOrderPriceArray = []
    closeOrderPriceArray = []

    if gt.setOrders():
        currentSize = abs(gt.getPositionSize())
        sizeDiff =  params['maxPositionSize'] - currentSize

        if sizeDiff >= 0  and gt.checkSleep():
            openOrderPriceArray = gt.getOpenOrderPriceArray(sizeDiff)

            for eachPrice in openOrderPriceArray:
                if gt.notOrderAlreadyPlaced(eachPrice):
                    gt.placeOrder(helper[params['mode']]['open'], params['sizePerOrder'], eachPrice)
                    count = count + 1

                    if count % 10 == 0:
                        time.sleep(1)
                    
        if currentSize > 0  and gt.checkSleep():
            closeOrderPriceArray = gt.getCloseOrderPriceArray(currentSize)

            for eachPrice in closeOrderPriceArray:
                if gt.notOrderAlreadyPlaced(eachPrice):
                    gt.placeOrder(helper[params['mode']]['close'], params['sizePerOrder'], eachPrice)

                    count = count + 1

                    if count % 10 == 0:
                        time.sleep(1)

        gt.cleanOrders(openOrderPriceArray + closeOrderPriceArray)

def perform_all():
    while True:
        perform_once()
        time.sleep(params['sleepTime'])

if __name__ == "__main__":
    perform_all()