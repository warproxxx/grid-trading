import argparse
from liveTrader import liveTrading
import time
import pandas as pd
import threading

parser = argparse.ArgumentParser("Grid Trader")
parser.add_argument("--divNumber", help="Divisible price points to check at", type=int, default=10)
parser.add_argument("--orderAbove", help="Number of orders above current price", type=int, default=50)
parser.add_argument("--orderBelow", help="Number of orders below current price", type=int, default=50)
parser.add_argument("--startPrice", help="Only starts if the current price is in the given range inputted here", type=int, default=-1)
parser.add_argument("--leverage", help="Leverage to use", type=int, default=10)


params = vars(parser.parse_args())



lt = liveTrading()
lt.set_leverage()

def add_order(order_type, amount, price):
    t = threading.Thread(target=(lt.limit_trade), args=(order_type, amount, price,))

def perform_once(reset=False):
    obook = lt.get_orderbook()
    curr_price = int(round(obook['best_bid'], -1))

    if params['startPrice'] == -1 or curr_price == params['startPrice']:

        if reset == True:
            lt.close_all_orders()

        orders_df = pd.DataFrame(lt.get_all_orders())
        amt = lt.get_balance() * params['leverage']

        start_time = time.time()

        if len(orders_df) > 0:
            orders = orders_df[['price', 'order_id']].set_index('price').T.to_dict()
        else:
            orders = {}

        
        total = obook['best_bid'] * amt
        totalOrders = params['orderAbove'] + params['orderBelow']

        single_size = (total/totalOrders)/obook['best_bid']
        print(single_size)
        

        print("Starting at {}".format(curr_price))

        above_points = [i for i in range(curr_price+params['divNumber'], int(curr_price+((params['orderAbove'] + 1) * params['divNumber'])), params['divNumber'])]
        below_points = [i for i in range(curr_price+params['divNumber'], int(curr_price-((params['orderBelow'] + 1) * params['divNumber'])), params['divNumber'] * -1)]
        
        
        for point in above_points:
            try:
                del orders[point]
            except:
                pass

        for point in below_points:
            try:
                del orders[point]
            except:
                pass

        for i in above_points:
            if i not in orders:
                add_order('sell', single_size, i)

        for i in below_points:
            if i not in orders:
                add_order('buy', single_size, i)

        print(time.time() - start_time)

perform_once()