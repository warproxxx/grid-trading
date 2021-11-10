import ccxt

import os
import time
import numpy as np
import json
import pandas as pd
import datetime
import decimal
import inspect
import sys

class liveTrading():
    def __init__(self, symbol='BTC/USD', lev=3, params={}):
        self.symbol = symbol

        self.lev = lev
        self.symbol_here = ""
        self.threshold_tiggered = False
        self.attempts = 5

        apiKey = os.getenv('BYBIT_ID')
        apiSecret = os.getenv('BYBIT_SECRET')


        self.exchange = ccxt.bybit({
                        'apiKey': apiKey,
                        'secret': apiSecret,
                        'enableRateLimit': True,
                    })

        self.symbol_here = symbol.replace("/", "")

    
        lm = self.exchange.load_markets()
        self.increment = lm[self.symbol]['precision']['amount']

        number_str = '{0:f}'.format(self.increment)
        self.round_places = len(number_str.split(".")[1])

    def set_leverage(self):
        count = 0
        
        while count < 5:
            try:
                stats = self.exchange.v2_private_post_position_leverage_save({'symbol': self.symbol_here, 'leverage': str(self.lev)})
                stats = self.exchange.v2_private_post_position_switch_isolated({'symbol': self.symbol_here, 'is_isolated': False, 'sell_leverage': str(self.lev), 'buy_leverage': str(self.lev)})

                break

            except Exception as e:
                print(str(e))
                if "many requests" in str(e).lower():
                    print("Too many requests in {}".format(inspect.currentframe().f_code.co_name))
                    break
                

                if ("same to the old" in str(e)):
                    break
                if ("balance not enough" in str(e)):
                    break
                
                count = count + 1
    
    def get_all_orders(self):
        return self.get_unfilled_orders() + self.get_partial_orders()

    def get_unfilled_orders(self):
        return self.exchange.v2_private_get_order_list({'symbol': 'BTCUSD', 'order_status': 'New'})['result']['data']

    def get_partial_orders(self):
        return self.exchange.v2_private_get_order_list({'symbol': 'BTCUSD', 'order_status': 'PartiallyFilled'})['result']['data']

    def close_all_orders(self, close_stop=False):
        self.exchange.cancel_all_orders(symbol=self.symbol)

    def get_orderbook(self):
        orderbook = {}

        book = self.exchange.fetch_order_book(self.symbol)
        orderbook['best_ask'] =  book['asks'][0][0]
        orderbook['best_bid'] = book['bids'][0][0]

        return orderbook

    def cancel_order(self, order_id):
        self.exchange.v2_private_post_order_cancel({'symbol': self.symbol_here, 'order_id': order_id})

    def get_position(self):
        for lp in range(self.attempts):
            try:
                pos = self.exchange.v2_private_get_position_list(params={'symbol': self.symbol_here})['result']

                if float(pos['size']) == 0:
                    return 'NONE', 0, 0
                else:
                    if float(pos['size']) < 0:
                        current_pos = "SHORT"
                    else:
                        current_pos = "LONG"

                return current_pos, float(pos['entry_price']), float(pos['size'])
                
            except ccxt.BaseError as e:
                if "many requests" in str(e).lower():
                    print("Too many requests in {}".format(inspect.currentframe().f_code.co_name))
                    break
                
                print("Error in get position: {}".format(str(e)))
                time.sleep(1)
                pass


    def get_balance(self):
        for lp in range(self.attempts):
            try:
                return float(self.exchange.fetch_balance()['info']['result']['BTC']['equity'])
            except Exception as e:
                print(str(e))


    def limit_trade(self, order_type, amount, price):
        if amount > 0:
            print("Sending limit {} order for {} of size {} @ {} on {} in {}".format(order_type, self.symbol, amount, price, 'bybit', datetime.datetime.utcnow()))

            params = {
                        'time_in_force': 'PostOnly'
            }

            order = self.exchange.create_order(self.symbol, type='limit', side=order_type, amount=amount, price=price, params=params)
            
            try:
                order_id = order['info']['order_id']
            except:
                order_id = order['info'][0]['order_id']

            order = self.exchange.fetch_order(order_id, symbol=self.symbol)

            if order['info']['order_status'] == 'Cancelled':
                return self.limit_trade(order_type, amount, price)

            return order
        else:
            print("Doing a zero trade")
            return []

    def send_limit_order(self, order_type):
        for lp in range(self.attempts):
            try:
                amount, price = self.get_max_amount(order_type)

                if amount == 0:
                    return [], 0

                order = self.limit_trade(order_type, amount, price)

                return order, price
            except ccxt.BaseError as e:
                print(e)
                pass

    
    def market_trade(self, order_type, amount):
        if amount > 0:
            print("Sending market {} order for {} of size {} on {} in {}".format(order_type, self.symbol, amount, 'bybit', datetime.datetime.utcnow()))

            order = self.exchange.create_order(self.symbol, 'market', order_type, amount, None)
            return order
            
        else:
            print("Doing a zero trade")
            return []