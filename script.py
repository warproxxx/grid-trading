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

parser = argparse.ArgumentParser("Grid Trader")
parser.add_argument("--divNumber", help="Divisible price points to check at", type=int, default=10)
parser.add_argument("--maxOrder", help="Size of single order", type=int, default=10)
parser.add_argument("--orderAbove", help="Number of orders above current price", type=int, default=20)
parser.add_argument("--orderBelow", help="Number of orders below current price", type=int, default=20)
parser.add_argument("--startPrice", help="Only starts if the current price is in the given range inputted here", type=int, default=-1)
parser.add_argument("--sleepTime", help="Seconds delayed", type=int, default=60)

params = vars(parser.parse_args())

lt = liveTrading(lev=25)
lt.set_leverage()

def add_order(order_type, amount, price):
    t = threading.Thread(target=(lt.limit_trade), args=(order_type, amount, price,))
    t.start()

def remove_order(order_id):
    t = threading.Thread(target=(lt.cancel_order), args=(order_id,))
    t.start()

def perform_once(reset=False):
    obook = lt.get_orderbook()

    curr_up = int(round_up(obook['best_bid'], params['divNumber']))
    curr_down = int(round_down(obook['best_bid'], params['divNumber']))

    if params['startPrice'] == -1 or (params['startPrice'] >= curr_down and params['startPrice'] <= curr_up):

        if reset == True:
            lt.close_all_orders()

        orders_df = pd.DataFrame(lt.get_all_orders())

        start_time = time.time()

        if len(orders_df) > 0:
            orders = orders_df[['price', 'order_id']].set_index('price').T.to_dict()
        else:
            orders = {}

        print("Starting at {} {}".format(curr_up, curr_down))

        above_points = [i for i in range(curr_up, int(curr_up+((params['orderAbove']) * params['divNumber'])), params['divNumber'])]
        below_points = [i for i in range(curr_down, int(curr_down-((params['orderBelow']) * params['divNumber'])), params['divNumber'] * -1)]

        for order in orders:
            if int(order) not in above_points and int(order) not in below_points:

                print("Removing {}".format(order))
                remove_order(orders[order]['order_id'])


        for i in above_points:
            if i not in orders:
                add_order('sell', params['maxOrder'], i)

        for i in below_points:
            if i not in orders:
                add_order('buy', params['maxOrder'], i)



        print(time.time() - start_time)

def perform_all():
    curr_count = 0

    while True:
        if (curr_count == 60):
            curr_count = 0
            perform_once(reset=True)
        else:
            perform_once()

        time.sleep(params['sleepTime'])
        curr_count = curr_count + 1

if __name__ == "__main__":
    perform_all()