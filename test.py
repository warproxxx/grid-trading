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

sizeDiff =  params['maxPositionSize']
print(gt.getLongOrderPriceArray(sizeDiff))