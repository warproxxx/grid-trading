import argparse
from liveTrader import liveTrading

parser = argparse.ArgumentParser("Grid Trader")
parser.add_argument("--divNumber", help="Divisible price points to check at", type=int, default=10)
parser.add_argument("--orderAbove", help="Number of orders above current price", type=int, default=50)
parser.add_argument("--orderBelow", help="Number of orders below current price", type=int, default=50)
parser.add_argument("--startPrice", help="Only starts if the current price is in the given range inputted here", type=int, default=-1)
parser.add_argument("--leverage", help="Leverage to use", type=int, default=10)


params = vars(parser.parse_args())
print(params)

lt = liveTrading()
lt.close_all_orders()
obook = lt.get_orderbook()

amt = lt.get_balance() * params['leverage']
total = obook['best_bid'] * amt
totalOrders = params['orderAbove'] + params['orderBelow']

single_size = (total/totalOrders)/obook['best_bid']
print(single_size)
curr_price = round(obook['best_bid'], -1)

print(curr_price)

# if params['startPrice'] == -1