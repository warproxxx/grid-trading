import argparse
from gridTrader import gridTrader


parser = argparse.ArgumentParser("script.py")
    
parser.add_argument("--maxPositionSize", help="Max Position Size", type=int, default=50)
parser.add_argument("--sizePerOrder", help="Size per order", type=int, default=1)
parser.add_argument("--timeframe", help="Run time in miniutes", type=int, default=240)
parser.add_argument("--sleepTime", help="Seconds delayed", type=int, default=15)
parser.add_argument("--spread", help="Spread between orders", type=int, default=10)
parser.add_argument("--mode", help="long or short", type=str, default="short")

gt = gridTrader(vars(parser.parse_args()))
params = gt.get_processed_vars()

print(gt.orders)