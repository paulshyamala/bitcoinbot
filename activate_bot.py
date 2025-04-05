import requests
import time
from database import DatabaseManager
from api import BinanceAPI
from utils import Utils

class ActivateBot:
    def __init__(self, ws_class, bi_class):
        self.ws_class = ws_class
        self.bi_class = bi_class
        self.db = DatabaseManager()
    """
    def place_order(self):
        
        self.rsi_indicator = BinanceRSI()
        if self.rsi_flag == 0:
            print("red image")
        else:
            print("green")"
            
    
    """       
    def buy_btc(self):
        self.buy_btc_price = 0
        combined_flag = self.ws_class.bi.rsi_flag + self.ws_class.bi.macd_flag + self.ws_class.bi.st_flag
        if True or combined_flag >= 2:
            print("time to buy")
            self.balance = self.ws_class.db.get_account_balance(self.ws_class.username)
            print("account balabce before", self.balance)
            self.trading_amount = self.balance * ((self.ws_class.thresholds["invest_thres"][0])/100)
            current_date = Utils.get_date()
            self.buy_btc_price = BinanceAPI.get_price_on_day(current_date)
            print("bought", self.trading_amount, "$ amount of bitcoin at", self.buy_btc_price)
            self.db.update_trade_history_buy(self, self.bi_class, self.ws_class.username)

    def sell_btc(self):
        self.sell_btc_price = 0
        combined_flag = self.ws_class.bi.rsi_flag + self.ws_class.bi.macd_flag + self.ws_class.bi.st_flag
        if True or combined_flag <= 1:
            print("time to sell")
            current_date = Utils.get_date()
            self.sell_btc_price = BinanceAPI.get_price_on_day(current_date)
            per_diff = ((self.sell_btc_price - self.buy_btc_price)/self.buy_btc_price)
            multiplier_value = 1+per_diff
            self.new_trading_amount = multiplier_value*self.trading_amount

            self.profit_loss = self.new_trading_amount - self.trading_amount

            self.ws_class.db.update_account_balance(self.ws_class.username, self.profit_loss)
            self.balance = self.ws_class.db.get_account_balance(self.ws_class.username)
            print("sold", self.new_trading_amount, "$ of bitcoin at", self.sell_btc_price)
            print("profit/loss=", self.profit_loss)
            print("account balabce after", self.balance)
            self.db.update_trade_history_sell(self,self.bi_class,  self.ws_class.username)



    # def get_ticker_price(self, symbol="BTCUSDT"):

    #     BASE_URL = "https://testnet.binance.vision/api"
    #     """Fetch the latest price for a given symbol from Binance Testnet."""
    #     endpoint = f"{BASE_URL}/v3/ticker/price"
    #     params = {"symbol": symbol}
    #     response = requests.get(endpoint, params=params)
    #     if response.status_code == 200:
    #         data = response.json()
    #         return float(data["price"])
    #     else:
    #         return f"Error: {response.status_code}, {response.text}"

