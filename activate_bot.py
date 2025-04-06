from database import DatabaseManager
from api import BinanceAPI
from utils import Utils

class ActivateBot:
    """
    ActivateBot controls the decision-making logic of when to buy or sell Bitcoin
    based on technical indicators like RSI, MACD, and Supertrend.

    Attributes:
        user_obj: The user object containing user-specific data including username,
                  database access, and investment thresholds.
        ws_class: The websocket or wrapper class instance providing indicator flags.
        bi_class: The technical indicators (RSI, MACD, ST) class instance used for
                  storing or analyzing historical signal data.
    """

    def __init__(self, user_obj, ws_class, bi_class):
        """
        Initializes the trading bot with user and indicator references.

        Args:
            user_obj: The user instance that includes username and database interface.
            ws_class: Class containing real-time indicator flags (RSI, MACD, ST).
            bi_class: Class used for maintaining technical indicator data.
        """
        self.user_obj = user_obj
        self.ws_class = ws_class
        self.bi_class = bi_class

    def buy_btc(self, given_date):
        """
        Executes a buy order for Bitcoin if 2 or more technical indicators are positive.

        Steps:
        - Checks if at least two out of three flags (RSI, MACD, ST) suggest buying.
        - Retrieves the user's current account balance.
        - Determines trading amount based on investment threshold.
        - Fetches the BTC price on the given date using BinanceAPI.
        - Updates the trade history for a buy transaction.

        Args:
            given_date (str): Date string in 'YYYY-MM-DD' format used to fetch historical BTC price.
        """
        self.buy_btc_price = 0
        combined_flag = 0
        
        # Check individual buy signals
        if self.ws_class.bi.rsi_flag > 0:
            combined_flag += 1
        if self.ws_class.bi.macd_flag > 0:
            combined_flag += 1
        if self.ws_class.bi.st_flag > 0:
            combined_flag += 1

        # Execute buy if at least 2 indicators are positive
        if combined_flag >= 2:
            print("time to buy")
            self.balance = self.user_obj.db.get_account_balance(self.user_obj.username)
            print("account balabce before", self.balance)
            self.trading_amount = self.balance * ((self.user_obj.thresholds["invest_thres"][0]) / 100)
            self.buy_btc_price = BinanceAPI.get_price_on_day(given_date)
            print("bought", self.trading_amount, "$ amount of bitcoin at", self.buy_btc_price)
            self.user_obj.db.update_trade_history_buy(given_date, self.user_obj, self, self.bi_class)

    def sell_btc(self, given_date):
        """
        Executes a sell order for Bitcoin if 2 or more technical indicators are negative.

        Steps:
        - Checks if at least two out of three flags (RSI, MACD, ST) suggest selling.
        - Calculates percentage difference and adjusts trading amount.
        - Computes profit/loss.
        - Updates the user's account balance and trade history.

        Args:
            given_date (str): Date string in 'YYYY-MM-DD' format used to fetch historical BTC price.
        """
        self.sell_btc_price = 0
        combined_flag = 0

        # Check individual sell signals
        if self.ws_class.bi.rsi_flag < 0:
            combined_flag += 1
        if self.ws_class.bi.macd_flag < 0:
            combined_flag += 1
        if self.ws_class.bi.st_flag < 0:
            combined_flag += 1

        # Execute sell if at least 2 indicators are negative
        if combined_flag >= 2:
            print("time to sell")
            self.sell_btc_price = BinanceAPI.get_price_on_day(given_date)
            per_diff = ((self.sell_btc_price - self.buy_btc_price) / self.buy_btc_price)
            multiplier_value = 1 + per_diff
            self.new_trading_amount = multiplier_value * self.trading_amount

            self.profit_loss = self.new_trading_amount - self.trading_amount

            self.user_obj.db.update_account_balance(self.user_obj.username, self.profit_loss)
            self.balance = self.user_obj.db.get_account_balance(self.user_obj.username)
            print("sold", self.new_trading_amount, "$ of bitcoin at", self.sell_btc_price)
            print("profit/loss=", self.profit_loss)
            print("account balabce after", self.balance)
            self.user_obj.db.update_trade_history_sell(given_date, self.user_obj, self, self.bi_class)
