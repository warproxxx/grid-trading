import argparse
from liveTrader import liveTrading
import time
import pandas as pd
import threading
import math

#50 per seconds

def round_up(x, divNumber):
    return int(math.ceil(x / divNumber)) * divNumber

def round_down(x, divNumber):
    return int(math.floor(x / divNumber)) * divNumber

parser = argparse.ArgumentParser("script.py")
parser.add_argument("--divNumber", help="Divisible price points to check at", type=int, default=10)
parser.add_argument("--maxOrder", help="Size of single order", type=int, default=1)
parser.add_argument("--orderAbove", help="Number of orders above current price", type=int, default=50)
parser.add_argument("--orderBelow", help="Number of orders below current price", type=int, default=50)
parser.add_argument("--startPrice", help="Only starts if the current price is in the given range inputted here", type=int, default=-1)
parser.add_argument("--sleepTime", help="Seconds delayed", type=int, default=60)

params = vars(parser.parse_args())
startPrice = params['startPrice']

lt = liveTrading(lev=25)
lt.set_leverage()

obook = lt.get_orderbook()

if startPrice == -1:
    startPrice = obook['best_bid']

curr_up = int(round_up(startPrice, params['divNumber']))
curr_down = int(round_down(startPrice, params['divNumber']))

above_points = [i for i in range(curr_up, int(curr_up+((params['orderAbove']) * params['divNumber'])), params['divNumber'])]
below_points = [i for i in range(curr_down, int(curr_down-((params['orderBelow']) * params['divNumber'])), params['divNumber'] * -1)]
all_points = below_points + above_points

def add_order(order_type, amount, price):
    t = threading.Thread(target=(lt.limit_trade), args=(order_type, amount, price,))
    t.start()

def remove_order(order_id):
    t = threading.Thread(target=(lt.cancel_order), args=(order_id,))
    t.start()

def perform_once(reset=False):
    obook = lt.get_orderbook()

    orders_df = pd.DataFrame(lt.get_all_orders())

    start_time = time.time()

    if len(orders_df) > 0:
        orders = orders_df[['price', 'order_id']].set_index('price').T.to_dict()
    else:
        orders = {}

    print(orders)

    count = 0

    for i in all_points:
        if str(i) not in orders:
            if i > obook['best_bid']:
                otype = 'sell'
            else:
                otype = 'buy'
            add_order(otype, params['maxOrder'], i)
            count = count + 1

            if count % 10 == 0:
                time.sleep(1)

    print(time.time() - start_time)

def perform_all():

    while True:
        perform_once()
        time.sleep(params['sleepTime'])

if __name__ == "__main__":
    perform_all()