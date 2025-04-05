import sqlite3
import pandas as pd
from utils import Utils

#DATABASE_PATH = '/Users/praneeth/sqlite3/bitcoin.db'
#DATABASE_PATH = "C:/Users/User/OneDrive - University of Toronto/Desktop/OneDrive - GEMS EDUCATION/CryptoBot/assets/bitcoin.db"
DATABASE_PATH = "assets/bitcoin.db"
class DatabaseManager:
    """Handles database operations for user management and balances."""

    def __init__(self):
        try:

            """Initializes the database connection."""
            self.conn = sqlite3.connect(DATABASE_PATH)
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
        Retrieves the SALT_KEY from the database.

        Returns:
            str: The salt key.
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
                                (username, hashed_password, 0))
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
        Adds the specified amount to the user's existing account balance.

        Args:
            username (str): The username.
            amount (float): The amount to add to the balance.

        Returns:
            bool: True if update was successful, False otherwise.
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
            if new_balance<5000 and new_balance>500:
                # Update the balance
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
        
        try:
            self.thresholds = pd.read_sql_query(f"SELECT * FROM risk_thresholds WHERE risk_level = {risk_level}", self.conn)
            #print(self.thresholds)
            if not self.thresholds.empty:
                self.invest_thres = self.thresholds["invest_thres"][0]
                #print(self.invest_thres)
                return self.thresholds
            
        except sqlite3.Error as error:
            print(f"Database error: {error}")
            return 
        
    def update_trade_history_buy(self, ab_class, bi_class, username):
        """
        Updates the trade history with a buy trade. Uses data from the 
        instance's attributes, likely related to a websocket connection.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Fetch user ID based on username
            user_id_df = pd.read_sql_query(
                "SELECT user_id FROM user_profile WHERE username = ?",
                self.conn, params=(username,)  # Add comma for single-element tuple
            )
            user_id = int(user_id_df['user_id'][0])
            print("Biy", username, user_id)
            # Insert trade data into trade_history table

            self.cursor.execute(
                """
                INSERT INTO trade_history (
                    user_id, money_in, risk_level, buying_time, buy_price, balance_before, 
                    rsi_buy, macd_buy, supertrend_buy, 
                    rsi_flag_buy, macd_flag_buy, supertrend_flag_buy
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?);
                """,
                (
                    user_id, ab_class.trading_amount, bi_class.risk_level, Utils.get_localtime(),
                    ab_class.buy_btc_price, ab_class.balance, bi_class.rsi, bi_class.macd,
                    bi_class.supertrend, bi_class.rsi_flag, bi_class.macd_flag,
                    bi_class.st_flag
                )
            )
          
            self.conn.commit()
            return True

        except sqlite3.Error as error:
            print(f"Database error: {error}")
            self.conn.rollback() # Rollback on error
            return False
        
    def update_trade_history_sell(self , ab_class, bi_class, username):
        """
        Updates the trade history with a buy trade. Uses data from the 
        instance's attributes, likely related to a websocket connection.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            user_id_df = pd.read_sql_query(
                "SELECT user_id FROM user_profile WHERE username = ?",
                self.conn, params=(username,)  # Add comma for single-element tuple
            )
            user_id = int(user_id_df['user_id'][0])
            print("sell", username, user_id)
            # Fetch user ID based on username
            trade_id_df = pd.read_sql_query(
                "SELECT max(trade_id) as trade_id FROM trade_history WHERE user_id = ?",
                self.conn, params=(user_id,)  # Add comma for single-element tuple
            )
            trade_id = int(trade_id_df['trade_id'][0])

            # Insert trade data into trade_history table
            self.cursor.execute(
            """
            UPDATE trade_history 
            SET selling_time = ?, sell_price = ?, profit_loss = ?, balance_after = ?,
                rsi_sell = ?, macd_sell = ?, supertrend_sell = ?,
                rsi_flag_sell = ?, macd_flag_sell = ?, supertrend_flag_sell = ?
            WHERE trade_id = ?;
            """,
            (
                Utils.get_localtime(),
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
            )
            )
            self.conn.commit()
            return True

        except sqlite3.Error as error:
            print(f"Database error: {error}")
            self.conn.rollback() # Rollback on error
            return False
    
    def log_event(self, username, event_type, comments=None):
        """
        Inserts a record into the application_logs table.
        
        :param user_id: Integer ID of the user
        :param event_type: One of ('LOGIN', 'LOGOUT', 'CHANGE_PASSWORD')
        :param comments: Optional string comments about the event
        """
        # Current timestamp in YYYY-MM-DD HH:MM:SS format
        try:
            user_id_df = pd.read_sql_query(
                "SELECT user_id FROM user_profile WHERE username = ?",
                self.conn, params=(username,)  # Add comma for single-element tuple
            )
            user_id = int(user_id_df['user_id'][0])
            event_time = Utils.get_localtime()
            

            # Insert the log record
            query = """
                INSERT INTO application_logs (user_id, event_type, event_time, comments)
                VALUES (?, ?, ?, ?)
            """
            self.cursor.execute(query, (user_id, event_type, event_time, comments))
            
            # Commit changes and close connection
            self.conn.commit()
            
        except sqlite3.Error as error:
            print(f"Database error: {error}")
            self.conn.rollback() # Rollback on error
            return False
        
    def get_trade_history(self, username):
        """
        Updates the trade history with a buy trade. Uses data from the 
        instance's attributes, likely related to a websocket connection.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Fetch user ID based on username
            user_id_df = pd.read_sql_query(
                "SELECT user_id FROM user_profile WHERE username = ?",
                self.conn, params=(username,)  # Add comma for single-element tuple
            )
            user_id = int(user_id_df['user_id'][0])
            print("Biy", username, user_id)
            # Insert trade data into trade_history table

            trade_df = pd.read_sql_query(
                "SELECT * FROM trade_history WHERE user_id = ?",
                self.conn, params=(user_id,)  # Add comma for single-element tuple
            )
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
        Inserts a record into the application_logs table.
        
        :param user_id: Integer ID of the user
        :param event_type: One of ('LOGIN', 'LOGOUT', 'CHANGE_PASSWORD')
        :param comments: Optional string comments about the event
        """
        # Current timestamp in YYYY-MM-DD HH:MM:SS format
        try:
            user_id_df = pd.read_sql_query(
                "SELECT user_id FROM user_profile WHERE username = ?",
                self.conn, params=(username,)  # Add comma for single-element tuple
            )
            user_id = int(user_id_df['user_id'][0])
            account_date = Utils.get_localtime()
            

            # Insert the log record
            query = """
                INSERT INTO account_history (user_id, account_date, account_balance)
                VALUES (?, ?, ?)
            """
            self.cursor.execute(query, (user_id, account_date, account_balance))
            
            # Commit changes and close connection
            self.conn.commit()
            
        except sqlite3.Error as error:
            print(f"Database error: {error}")
            self.conn.rollback() # Rollback on error
            return False
        
    def get_account_history(self, username):
        try:
            user_id_df = pd.read_sql_query(
                "SELECT user_id FROM user_profile WHERE username = ?",
                self.conn, params=(username,)  # Add comma for single-element tuple
            )
            user_id = int(user_id_df['user_id'][0])
            
            account_df = pd.read_sql_query(
                "SELECT * FROM account_history WHERE user_id = ?",
                self.conn, params=(user_id,)  # Add comma or single-element tuple
            )
            
            if len(account_df) <= 0:
                print("No history available")
                return False, None
            else:
                return True, account_df
            
        except sqlite3.Error as error:
            print(f"Database error: {error}")
            return None