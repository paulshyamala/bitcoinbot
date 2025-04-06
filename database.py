import sqlite3
import pandas as pd
from utils import Utils

# Path to the database files
DATABASE_PATH = "assets/bitcoin.db"
DATABASE_TEST_PATH = "assets/bitcoin_test.db"

class DatabaseManager:
    """
    Handles database operations for user management and balances in a cryptocurrency trading application.
    It manages user data, account balances, trade history, and logs events in the system.
    """

    def __init__(self, trading_preference):
        """
        Initializes the database connection based on the trading preference.
        
        Args:
            trading_preference (bool): Determines which database to connect to (main or test).
        """
        try:
            self.trading_preference = trading_preference
            if (trading_preference):
                self.conn = sqlite3.connect(DATABASE_PATH)  # Connect to main database
            else:
                self.conn = sqlite3.connect(DATABASE_TEST_PATH)  # Connect to test database
            self.cursor = self.conn.cursor()
        except sqlite3.Error as error:
            print(f"Unable to Connect database manager: {error}")
            return 

    def close_connection(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()

    def get_salt_key(self) -> str:
        """
        Retrieves the SALT_KEY from the database, which is used for password hashing.
        
        Returns:
            str: The salt key if found, else an empty string.
        """
        try:
            self.thresholds = pd.read_sql_query("SELECT config_value FROM bitcoin_config WHERE config_code = 'SALT_KEY'", self.conn)
            return self.thresholds['config_value'][0] if not self.thresholds.empty else ""
        except sqlite3.Error as error:
            print(f"Database error: {error}")
            return ""

    def add_user(self, username: str, hashed_password: str) -> bool:
        """
        Adds a new user to the database if the username is unique.
        
        Args:
            username (str): The username.
            hashed_password (str): The hashed password.

        Returns:
            bool: True if the user was added successfully, False if the username already exists.
        """
        try:
            self.thresholds = pd.read_sql_query("SELECT COUNT(*) as user_count FROM user_profile WHERE username = ?", self.conn, params=(username,))
            user_count = self.thresholds['user_count'][0]

            if user_count > 0:
                return False  # Username already exists

            self.cursor.execute("INSERT INTO user_profile(username, hashed_password, account_balance) VALUES (?, ?, ?);",
                                (username, hashed_password, 0))  # Insert user into the database
            self.conn.commit()
            return True
        except sqlite3.Error as error:
            print(f"Database error: {error}")
            return False

    def get_user(self, username: str) -> pd.DataFrame:
        """
        Fetches user details from the database.
        
        Args:
            username (str): The username to search for.
        
        Returns:
            pd.DataFrame: A DataFrame containing user data.
        """
        try:
            return pd.read_sql_query("SELECT * FROM user_profile WHERE username = ?", self.conn, params=(username,))
        except sqlite3.Error as error:
            print(f"Database error: {error}")
            return pd.DataFrame()

    def update_account_balance(self, username: str, amount: float):
        """
        Updates the user's account balance by adding the specified amount.

        Args:
            username (str): The username.
            amount (float): The amount to add to the account balance.

        Returns:
            bool: True if the balance was updated successfully, False otherwise.
        """
        try:
            # Fetch the current balance
            self.cursor.execute("SELECT account_balance FROM user_profile WHERE username = ?", (username,))
            row = self.cursor.fetchone()
            
            if row is None:
                print("User not found.")
                return False, 0
            
            current_balance = row[0]
            new_balance = current_balance + amount
            self.balance = new_balance
            if new_balance < 20000 and new_balance > 500:  # Ensure balance is within valid range
                # Update the balance in the database
                self.cursor.execute("UPDATE user_profile SET account_balance = ? WHERE username = ?", (new_balance, username))
                self.conn.commit()
                self.log_event(username, 'BALANCE_UPDATE', f'topup = {amount} total balance = {new_balance}')
                self.update_account_history(username, new_balance)
                return True, new_balance
            else:
                return False, 0
        except sqlite3.Error as error:
            print(f"Database error: {error}")
            return False, 0
    
    def get_account_balance(self, username: str):
        """
        Fetches the current account balance for a user.
        
        Args:
            username (str): The username to fetch the balance for.
        
        Returns:
            float: The current balance of the user.
        """
        try:
            # Fetch the current balance
            self.cursor.execute("SELECT account_balance FROM user_profile WHERE username = ?", (username,))
            row = self.cursor.fetchone()
            
            if row is None:
                print("User not found.")
                return False, 0
            
            current_balance = row[0]
            return current_balance
        except sqlite3.Error as error:
            print(f"Database error: {error}")
            return False, 0

    def get_risk_thresholds(self, risk_level):
        """
        Fetches the risk thresholds for a given risk level from the database.

        Args:
            risk_level (int): The risk level (1, 2, or 3) to retrieve thresholds for.

        Returns:
            pd.DataFrame: A DataFrame containing the risk thresholds.
        """
        try:
            self.thresholds = pd.read_sql_query(f"SELECT * FROM risk_thresholds WHERE risk_level = {risk_level}", self.conn)
            if not self.thresholds.empty:
                self.invest_thres = self.thresholds["invest_thres"][0]
                return self.thresholds
        except sqlite3.Error as error:
            print(f"Database error: {error}")
            return 

    def update_trade_history_buy(self, given_date, user_obj, ab_class, bi_class):
        """
        Updates the trade history with a buy trade.

        Args:
            given_date (str): The date and time of the buy trade.
            user_obj (object): The user object containing user details.
            ab_class (object): The account balance class containing trading information.
            bi_class (object): The indicators class containing trading signals (e.g., RSI, MACD).
        
        Returns:
            bool: True if the trade history was updated successfully, False otherwise.
        """
        try:
            # Fetch user ID
            user_id_df = pd.read_sql_query("SELECT user_id FROM user_profile WHERE username = ?", self.conn, params=(user_obj.username,))
            user_id = int(user_id_df['user_id'][0])

            # Insert trade data into trade history
            self.cursor.execute("""
                INSERT INTO trade_history (
                    user_id, money_in, risk_level, buying_time, buy_price, balance_before, 
                    rsi_buy, macd_buy, supertrend_buy, 
                    rsi_flag_buy, macd_flag_buy, supertrend_flag_buy
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?);
            """, (
                user_id, ab_class.trading_amount, user_obj.risk_level, given_date,
                ab_class.buy_btc_price, ab_class.balance, bi_class.rsi, bi_class.macd,
                bi_class.supertrend, bi_class.rsi_flag, bi_class.macd_flag,
                bi_class.st_flag
            ))

            self.conn.commit()
            return True

        except sqlite3.Error as error:
            print(f"Database error: {error}")
            self.conn.rollback()  # Rollback on error
            return False

    def update_trade_history_sell(self, given_date, user_obj, ab_class, bi_class):
        """
        Updates the trade history with a sell trade.

        Args:
            given_date (str): The date and time of the sell trade.
            user_obj (object): The user object containing user details.
            ab_class (object): The account balance class containing trading information.
            bi_class (object): The indicators class containing trading signals (e.g., RSI, MACD).

        Returns:
            bool: True if the trade history was updated successfully, False otherwise.
        """
        try:
            # Fetch user ID
            user_id_df = pd.read_sql_query("SELECT user_id FROM user_profile WHERE username = ?", self.conn, params=(user_obj.username,))
            user_id = int(user_id_df['user_id'][0])

            # Fetch trade ID for the last trade
            trade_id_df = pd.read_sql_query(
                "SELECT max(trade_id) as trade_id FROM trade_history WHERE user_id = ?",
                self.conn, params=(user_id,)
            )
            trade_id = int(trade_id_df['trade_id'][0])

            # Update trade data in trade history
            self.cursor.execute("""
                UPDATE trade_history 
                SET selling_time = ?, sell_price = ?, profit_loss = ?, balance_after = ?,
                    rsi_sell = ?, macd_sell = ?, supertrend_sell = ?,
                    rsi_flag_sell = ?, macd_flag_sell = ?, supertrend_flag_sell = ?
                WHERE trade_id = ?;
            """, (
                given_date,
                ab_class.sell_btc_price,
                ab_class.profit_loss, 
                ab_class.balance,
                bi_class.rsi,
                bi_class.macd,  
                bi_class.supertrend,
                bi_class.rsi_flag,
                bi_class.macd_flag,
                bi_class.st_flag,
                trade_id  
            ))

            self.conn.commit()
            return True

        except sqlite3.Error as error:
            print(f"Database error: {error}")
            self.conn.rollback()  # Rollback on error
            return False
    
    def log_event(self, username, event_type, comments=None):
        """
        Logs an event into the application logs table.
        
        Args:
            username (str): The username associated with the event.
            event_type (str): The type of event (e.g., LOGIN, LOGOUT, CHANGE_PASSWORD).
            comments (str, optional): Any additional comments related to the event.
        
        Returns:
            bool: True if the event was logged successfully, False otherwise.
        """
        try:
            # Fetch user ID
            user_id_df = pd.read_sql_query("SELECT user_id FROM user_profile WHERE username = ?", self.conn, params=(username,))
            user_id = int(user_id_df['user_id'][0])
            event_time = Utils.get_localtime()  # Get the current local time

            # Insert log record into application_logs table
            query = """
                INSERT INTO application_logs (user_id, event_type, event_time, comments)
                VALUES (?, ?, ?, ?)
            """
            self.cursor.execute(query, (user_id, event_type, event_time, comments))
            self.conn.commit()

        except sqlite3.Error as error:
            print(f"Database error: {error}")
            self.conn.rollback()  # Rollback on error
            return False

    def get_trade_history(self, username):
        """
        Retrieves the trade history for a user.
        
        Args:
            username (str): The username to fetch the trade history for.
        
        Returns:
            pd.DataFrame: A DataFrame containing the user's trade history, or None if no history found.
        """
        try:
            # Fetch user ID
            user_id_df = pd.read_sql_query("SELECT user_id FROM user_profile WHERE username = ?", self.conn, params=(username,))
            user_id = int(user_id_df['user_id'][0])

            # Fetch trade history
            trade_df = pd.read_sql_query("SELECT * FROM trade_history WHERE user_id = ?", self.conn, params=(user_id,))

            if len(trade_df) <= 0:
                print("There are no records")
                return None
            else:
                return trade_df

        except sqlite3.Error as error:
            print(f"Database error: {error}")
            return None

    def update_account_history(self, username, account_balance):
        """
        Updates the account history with the new account balance.

        Args:
            username (str): The username associated with the account history.
            account_balance (float): The updated account balance.

        Returns:
            bool: True if the account history was updated successfully, False otherwise.
        """
        try:
            # Fetch user ID
            user_id_df = pd.read_sql_query("SELECT user_id FROM user_profile WHERE username = ?", self.conn, params=(username,))
            user_id = int(user_id_df['user_id'][0])
            account_date = Utils.get_localtime()  # Get the current local time

            # Insert account balance history record
            query = """
                INSERT INTO account_history (user_id, account_date, account_balance)
                VALUES (?, ?, ?)
            """
            self.cursor.execute(query, (user_id, account_date, account_balance))
            self.conn.commit()

        except sqlite3.Error as error:
            print(f"Database error: {error}")
            self.conn.rollback()  # Rollback on error
            return False

    def get_account_history(self, username):
        """
        Retrieves the account history for a user.

        Args:
            username (str): The username to fetch the account history for.
        
        Returns:
            pd.DataFrame: A DataFrame containing the user's account history.
        """
        try:
            # Fetch user ID
            user_id_df = pd.read_sql_query("SELECT user_id FROM user_profile WHERE username = ?", self.conn, params=(username,))
            user_id = int(user_id_df['user_id'][0])
            
            # Fetch account history
            account_df = pd.read_sql_query("SELECT * FROM account_history WHERE user_id = ?", self.conn, params=(user_id,))
            
            if len(account_df) <= 0:
                print("No history available")
                return False, None
            else:
                return True, account_df
            
        except sqlite3.Error as error:
            print(f"Database error: {error}")
            return None
