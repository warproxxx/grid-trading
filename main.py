import argparse
from utils import gridTrader
import time

parser = argparse.ArgumentParser("script.py")

parser.add_argument("--maxPositionSize", help="Max Position Size", type=int, default=50)
parser.add_argument("--sizePerOrder", help="Size per order", type=int, default=1)
parser.add_argument("--timeframe", help="Run time in miniutes", type=int, default=240)
parser.add_argument("--sleepTime", help="Seconds delayed", type=int, default=15)
parser.add_argument("--divNumber", help="Divisible Price points to check at", type=int, default=10)

gt = gridTrader(vars(parser.parse_args()))
params = gt.get_processed_vars()

def perform_once():
    buyOrderPriceArray = []
    sellOrderPriceArray = []

    currentSize = gt.getPositionSize()
    sizeDiff =  params['maxPositionSize'] - currentSize

    if sizeDiff >= 0  and gt.checkSleep():
        gt.setOrders()
        buyOrderPriceArray = gt.getLongOrderPriceArray(sizeDiff)

        for eachPrice in buyOrderPriceArray:
            if gt.notOrderAlreadyPlaced(eachPrice):
                gt.placeOrder('buy', params['sizePerOrder'], eachPrice)

    if currentSize > 0  and gt.checkSleep():
        sellOrderPriceArray = gt.getShortOrderPriceArray(currentSize)

        for eachPrice in sellOrderPriceArray:
            if gt.notOrderAlreadyPlaced(eachPrice):
                gt.placeOrder('sell', params['sizePerOrder'], eachPrice)

    gt.cleanOrders(buyOrderPriceArray + sellOrderPriceArray)

def perform_all():
    while True:
        perform_once()
        time.sleep(params['sleepTime'])

if __name__ == "__main__":
    perform_all()