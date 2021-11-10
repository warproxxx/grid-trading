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
lt.set_leverage()

def perform_once(reset=False):
    obook = lt.get_orderbook()
    curr_price = int(round(obook['best_bid'], -1))

    if params['startPrice'] == -1 or curr_price == params['startPrice']:

        if reset == True:
            lt.close_all_orders()

        orders_df = pd.DataFrame(lt.get_all_orders())
        
        amt = lt.get_balance() * params['leverage']
        total = obook['best_bid'] * amt
        totalOrders = params['orderAbove'] + params['orderBelow']

        single_size = (total/totalOrders)/obook['best_bid']
        print(single_size)
        

        print("Starting at {}".format(curr_price))

        for i in range(curr_price+params['divNumber'], int(curr_price+((params['orderAbove'] + 1) * params['divNumber'])), params['divNumber']):
            print(i)


        for i in range(curr_price+params['divNumber'], int(curr_price-((params['orderBelow'] + 1) * params['divNumber'])), params['divNumber'] * -1):
            print(i)

