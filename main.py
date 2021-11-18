import argparse
from utils import gridTrader

parser = argparse.ArgumentParser("script.py")

parser.add_argument("--maxPositionSize", help="Max Position Size", type=int, default=500)
parser.add_argument("--sizePerOrder", help="Size per order", type=int, default=10)
parser.add_argument("--orderDivNumber", help="Divisible price points to check at", type=int, default=25)
parser.add_argument("--timeframe", help="Run time in miniutes", type=int, default=240)
parser.add_argument("--sleepTime", help="Seconds delayed", type=int, default=15)
parser.add_argument("--divNumber", help="Divisible Price points to check at", type=int, default=10)

gt = gridTrader(vars(parser.parse_args()))
params = gt.get_processed_vars()

def perform_once():
    currentSize = gt.getPositionSize()
    sizeDiff =  params['maxPositionSize'] - currentSize

    if sizeDiff > 0  and gt.checkSleep():
        gt.setOrders()
        buyOrderPriceArray = gt.getLongOrderPriceArray(sizeDiff)

        for eachPrice in buyOrderPriceArray:
            if gt.notOrderAlreadyPlaced(eachPrice):
                gt.placeOrder('buy', params['sizePerOrder'], eachPrice)

    if sizeDiff > 0  and gt.checkSleep():
        sellOrderPriceArray = gt.getShortOrderPriceArray(currentSize)

        for eachPrice in orderPriceArray:
            if gt.notOrderAlreadyPlaced(eachPrice):
                gt.placeOrder('sell', params['sizePerOrder'], eachPrice)


    gt.cleanOrders(buyOrderPriceArray + sellOrderPriceArray)

def perform_all():
    while True:
        perform_once()
        time.sleep(params['sleepTime'])

if __name__ == "__main__":
    perform_all()