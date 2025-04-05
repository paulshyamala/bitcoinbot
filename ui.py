import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from auth import AuthManager
from database import DatabaseManager
import re
from btccschart import BTCCandlestickChart
from bot_indicators import BotIndicators
from activate_bot import ActivateBot
import time
import requests
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import matplotlib.dates as mdates
from api import BinanceAPI

class BasePage(tk.Tk):
    def __init__(self, title):
        super().__init__()
        self.title(title)
        self.attributes('-fullscreen', True)

    def navigate_to(self, page_class, *args):
        self.destroy()
        page_class(*args).mainloop()

class LoginPage(BasePage):
    def __init__(self):
        super().__init__("Login Page")
        self.auth = AuthManager()

        btn_style = {"font": ("Arial", 30), "width": 12, "height": 2}

        tk.Label(self, text="Username:", **btn_style).pack(pady=5)
        self.username_entry = tk.Entry(self, bd=5, font=("Arial", 30), width=20)
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Password:", **btn_style).pack(pady=5)
        self.password_entry = tk.Entry(self, show="*", bd=5, font=("Arial", 30), width=20)
        self.password_entry.pack(pady=5)

        self.status_label = tk.Label(self, text="")
        self.status_label.pack(pady=5)

        tk.Label(self, text = "Username Rules", font = ("Arial", 20)).place(relx = 0.2, rely = 0.78)
        tk.Label(self, text = "The first letter of username should be an alphabet", font = ("Arial", 15)).place(relx = 0.15, rely = 0.82)
        tk.Label(self, text = "Username should be between 8 and 12 characters", font = ("Arial", 15)).place(relx = 0.15, rely = 0.84)
        tk.Label(self, text = "Special characters are not allowed in the username", font = ("Arial", 15)).place(relx = 0.15, rely = 0.86)

        tk.Label(self, text = "Password Rules", font = ("Arial", 20)).place(relx = 0.75, rely = 0.78)
        tk.Label(self, text = "The password should contain atleast 1 capital letter", font = ("Arial", 15)).place(relx = 0.7, rely = 0.82)
        tk.Label(self, text = "The password should contain atleast 1 number", font = ("Arial", 15)).place(relx = 0.7, rely = 0.84)
        tk.Label(self, text = "The password should contain atleast 1 special character", font = ("Arial", 15)).place(relx = 0.7, rely = 0.86)
        tk.Label(self, text = "The password should contain atleast 8 character", font = ("Arial", 15)).place(relx = 0.7, rely = 0.88)


        tk.Button(self, text="Login", **btn_style, 
                  command=self.handle_login).place(relx=0.5, rely=0.5, anchor="center")

        tk.Button(self, text="Register", **btn_style, 
                  command=self.handle_register).place(relx=0.5, rely=0.6, anchor="center")
    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        message = self.auth.validate_login(username, password)
        self.status_label.config(text=message)

        if message == "Login Successful":
            self.auth.close()
            self.navigate_to(AccountPage, username)

    def validate_user(self, username: str, password: str) -> bool:
        # Username validation: at least 8 characters, starts with a letter, no special characters
        #if not re.fullmatch(r"^[A-Za-z][A-Za-z0-9]{7,}$", username):
          #  return False
        if not re.search(r"^[A-Za-z]", username):
            messagebox.showerror("Error", "The first letter of username should be an alphabet")
            return False
        if len(username) < 8 or len(username) > 12:
            messagebox.showerror("Error", "Username should be between 8 and 12 characters")
            return False
        if re.search(r"[!@#$%^&*(),.?\"\':{}|<>]", username):     
            messagebox.showerror("Error", "Special characters are not allowed in the username")
            return False

        
        # Password validation: at least 8 characters, one capital letter, one special character, one number
        if not re.search(r"[A-Z]", password):
            messagebox.showerror("Error", "The password should contain atleast 1 capital letter")
            return False
        if not re.search(r"[0-9]", password):
            messagebox.showerror("Error", "The password should contain atleast 1 number")
            return False
        if not re.search(r"[!@#$%^&*(),.?\"\':{}|<>]", password):
            messagebox.showerror("Error", "The password should contain atleast 1 special character")
            return False
        if len(password) < 8:
            messagebox.showerror("Error", "The password should contain atleast 8 characters")
            return False
        
        return True

    def handle_register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.validate_user(username, password):

            if self.auth.register_user(username, password): 
                self.status_label.config(text="Register Successful, Press login to continue")
            else:
                self.status_label.config(text="This username already exists, please choose a different username")
        else:
            print("Invalid user")

    def on_close(self):
        self.auth.close()
        self.destroy()

class AccountPage(BasePage):
    def __init__(self, username):
        super().__init__("Account Page")
        self.username = username
        self.db = DatabaseManager() 

        # Load and display logo
        self.btblogo = self.load_image("assets/btblogo.png", (125, 150))
        tk.Button(self, image=self.btblogo, command = self.go_homepage, borderwidth=0, highlightthickness=0, highlightbackground="black", activebackground="black").place(anchor="nw")

        tk.Label(self, text="Click here if you don't want to add money", font=("Arial", 20)).place(relx=0, rely=0.1, anchor="nw")

        # Display username with profile picture
        self.profilepic = self.load_image("assets/profile.png", (40, 40))
        tk.Label(self, text=username, image=self.profilepic, compound="left", font=("Arial", 30)).place(relx=1, rely=0, anchor="ne")

        tk.Label(self, text="How much money do you want to put in?", font=("Arial", 30)).place(relx=0.5, rely=0.4, anchor="center")

        self.accountbalance_entry = tk.Entry(self, bd=5, font=("Arial", 30), width=20)
        self.accountbalance_entry.place(relx=0.6, rely=0.5, anchor="center")

        btn_style = {"font": ("Arial", 30), "width": 12, "height": 2}
        tk.Label(self, text="Balance (in Dollars $)", font=("Arial", 30), bd=5, relief="solid").place(relx=0.4, rely=0.5, anchor="center")

        tk.Button(self, text="Confirm", **btn_style, 
                  command=self.add_balance).place(relx=0.5, rely=0.6, anchor="center")

    def go_homepage(self):
        self.navigate_to(HomePage, self.username)
        self.destroy()

    def load_image(self, path, size):
        """function to load and resize an image."""
        img = Image.open(path)
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    def add_balance(self):
        """Calls DatabaseManager to update the database with balance."""
        try:
            balance = float(self.accountbalance_entry.get())
            success, new_balance = self.db.update_account_balance(self.username, balance)
            if success:
                messagebox.showinfo("Success", f"Balance updated: ${new_balance:.2f}")
               
                self.navigate_to(HomePage, self.username)
                self.destroy()
                  # Close the window after confirmation

            else:
                messagebox.showerror("Error", "Failed to update balance. Account Balance should be between 500$ and 5000$")
        except ValueError:
            messagebox.showerror("Error", "Invalid input! Please enter a valid number.")

    def on_close(self):
        """Closes database connection when AccountPage is closed."""
        self.db.close_connection()
        self.destroy()

class HomePage(BasePage):
    def __init__(self, username):
        super().__init__("Home Page")
        self.username = username
        self.db = DatabaseManager()

        self.btblogo = self.load_image("assets/btblogo.png", (125, 150))
        tk.Label(self, image=self.btblogo).place(anchor="nw")

        self.profilepic = self.load_image("assets/profile.png", (40, 40))
        tk.Label(self, text=username, image=self.profilepic, compound="left", font=("Arial", 30)).place(relx=1, rely=0, anchor="ne")

        btn_style = {"font": ("Arial", 30), "width": 12, "height": 2}

        tk.Label(self, text = "Home", font = ("Arial", 60)).place(relx = 0.5, rely = 0.1, anchor = "center")

        tk.Button(self, text="Profile", **btn_style, command = self.profile).place(relx=0.35, rely=0.5, anchor= "center")
        tk.Button(self, text="Add Money", **btn_style, command = self.add_money).place(relx=0.5, rely=0.5, anchor="center")
        tk.Button(self, text="Trade History", **btn_style, command = self.trade_history).place(relx=0.65, rely=0.5, anchor="center")
        tk.Button(self, text="Activate Bot", font=("Arial", 30), command = self.activate_bot, width=12, height=2, highlightbackground="green", bd=5, relief="solid").place(relx=0.5, rely=0.8, anchor="center")

    def load_image(self, path, size):
        """function to load and resize an image."""
        img = Image.open(path)
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    
    def profile(self):
        self.navigate_to(ProfilePage, self.username)
        

    def add_money(self):
        self.navigate_to(AccountPage, self.username)
        self.destroy()

    def trade_history(self):
        self.navigate_to(TradeHistoryPage, self.username)
        self.destroy()
    
    def activate_bot(self):
        self.navigate_to(RiskPage, self.username)
        self.destroy()

class TradeHistoryPage(BasePage):
    title_mapping = {
        "trade_id": "Trade ID",
        "user_id": "User ID",
        "money_in": "Investment Amount",
        "risk_level": "Risk Level",
        "buying_time": "Buy Time",
        "selling_time": "Sell Time",
        "buy_price": "Buy Price",
        "sell_price": "Sell Price",
        "profit_loss": "Profit/Loss",
        "balance_before": "Balance Before",
        "balance_after": "Balance After",
        "rsi_buy": "RSI ",
        "macd_buy": "MACD ",
        "supertrend_buy": "Supertrend ",
        "rsi_sell": "RSI ",
        "macd_sell": "MACD ",
        "supertrend_sell": "Supertrend ",
        "rsi_flag_buy": "RSI  Signal",
        "macd_flag_buy": "MACD Signal",
        "supertrend_flag_buy": "Supertrend  Signal",
        "rsi_flag_sell": "RSI  Signal",
        "macd_flag_sell": "MACD  Signal",
        "supertrend_flag_sell": "Supertrend  Signal"
    }
    def __init__(self, username):
        super().__init__("Trade History Page")
        self.username = username
        self.db = DatabaseManager()

        # Load and display logo
        self.btblogo = self.load_image("assets/btblogo.png", (125, 150))
        tk.Button(self, image=self.btblogo, command = self.go_homepage, borderwidth=0, highlightthickness=0, highlightbackground="black", activebackground="black").place(anchor="nw")

        self.profilepic = self.load_image("assets/profile.png", (40, 40))
        tk.Label(self, text=username, image=self.profilepic, compound="left", font=("Arial", 30)).place(relx=1, rely=0, anchor="ne")

        tk.Label(self, text = "Trade History", font = ("Arial", 60)).place(relx = 0.5, rely = 0.1, anchor = "center")

        btn_style = {"font": ("Arial", 30), "width": 12, "height": 2}
        trade_df = self.db.get_trade_history(self.username)
        if trade_df is None:
            print("No trade history available")
        else:
            
            self.display_tradehistory(trade_df)

    def create_table(self, parent, df, title):
        frame = ttk.LabelFrame(parent, text=title)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tree = ttk.Treeview(frame)
        tree["columns"] = list(df.columns)
        tree.column("#0", width=0, stretch=tk.NO)  # Hide first empty column
        
        for col in df.columns:
            width = len(col)   # Adjust column width dynamically
            print(width)
            tree.column(col, anchor=tk.W, width=width)
            tree.heading(col, text=col, anchor=tk.W)
        
        for index, row in df.iterrows():
            tree.insert("", "end", values=list(row))
        
        tree.pack(fill=tk.BOTH, expand=True)

    def display_tradehistory(self, df):
        df = df.round(2)
        # Rename DataFrame columns
        df_buy = df[['trade_id', 'money_in', 'risk_level', 'buying_time','buy_price',  'balance_before', 'rsi_buy', 'macd_buy','supertrend_buy', 'rsi_flag_buy', 'macd_flag_buy', 'supertrend_flag_buy']].copy()
        df_sell = df[['trade_id','money_in', 'risk_level', 'selling_time', 'sell_price', 'profit_loss','balance_after', 'rsi_sell', 'macd_sell', 'supertrend_sell', 'rsi_flag_sell','macd_flag_sell', 'supertrend_flag_sell']].copy()

        df_buy.rename(columns=self.title_mapping, inplace=True)
        df_sell.rename(columns=self.title_mapping, inplace=True)



        # Create the main application window
        # root = tk.Tk()
        # root.title("Trade History")
        # root.geometry("1200x600")
        root =  ttk.Frame(self)
        #root.pack(fill=tk.BOTH, expand=True, padx=20, pady=10) 
        # root.place(relx=0.0015, rely=0.15, width=self.winfo_width(), height=self.winfo_height()) 
        root.place(relx=0.0015, rely=0.15, relwidth=0.98, relheight=0.75)

        self.create_table(root, df_buy, "Buy Transactions")
        self.create_table(root, df_sell, "Sell Transactions")

        # Function to create a table with adjustable column width


    

    def load_image(self, path, size):
        """function to load and resize an image."""
        img = Image.open(path)
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    
    def go_homepage(self):
        self.navigate_to(HomePage, self.username)
        self.destroy()

class ProfilePage(BasePage):
    def __init__(self, username):
        super().__init__("Profile Page")
        self.username = username
        self.db = DatabaseManager()
        account_valid, account_df = self.db.get_account_history(username)
        root =  ttk.Frame(self)
        #root.pack(fill=tk.BOTH, expand=True, padx=20, pady=10) 
        # root.place(relx=0.0015, rely=0.15, width=self.winfo_width(), height=self.winfo_height()) 
        root.place(relx=0.0015, rely=0.15, relwidth=0.5, relheight=0.7)
        self.parent = root

        self.btblogo = self.load_image("assets/btblogo.png", (125, 150))
        tk.Button(self, image=self.btblogo, command = self.go_homepage, borderwidth=0, highlightthickness=0, highlightbackground="black", activebackground="black").place(anchor="nw")

        self.profilepic = self.load_image("assets/profile.png", (40, 40))
        tk.Label(self, text=username, image=self.profilepic, compound="left", font=("Arial", 30)).place(relx=1, rely=0, anchor="ne")       

        tk.Label(self, text="Account Balance", font=("Arial", 30)).place(relx=0.8, rely=0.4, anchor="center")

        tk.Label(self, text = "Profile", font = ("Arial", 60)).place(relx = 0.5, rely = 0.1, anchor = "center")

        account_balance = round(self.db.get_account_balance(self.username), 5)
        tk.Label(self, text=f"{account_balance} $", font=("Arial", 30)).place(relx=0.8, rely=0.5, anchor="center")
        if account_valid == True:
            self.plot_equity_curve(account_df)
        else:
            print("No history available")

    def load_image(self, path, size):
        """function to load and resize an image."""
        img = Image.open(path)
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)    
    
    def go_homepage(self):
        self.navigate_to(HomePage, self.username)
        self.destroy()

    # def plot_equity_curve(self, account_df):
        
    #     fig = Figure(figsize=(12, 6))
    #     ax1 = fig.add_subplot(111)  # RSI
        

        
    #     # 🚀 No need to pass x values! Matplotlib automatically uses index positions

    #     # Plot RSI
    #     ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m-%Y"))

    #     # ax1.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    #     for label in ax1.get_xticklabels():
    #         label.set_rotation(45)
    #         label.set_horizontalalignment('right')

    #     account_df["account_date"] = pd.to_datetime(account_df["account_date"])
    #     x1 = account_df["account_date"].dt.date.tolist()
    #     y1 = account_df["account_balance"].tolist()
    #     ax1.plot(x1, y1, color="blue")
    #     ax1.set_title("Equity Curve")
    #     ax1.set_xlabel("")
    #     ax1.set_ylabel("Account Balance ($)")


    #     # Embed the Matplotlib figure in Tkinter
    #     self.canvas = FigureCanvasTkAgg(fig, master=self.parent)
    #     self.canvas.draw()
    #     self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_equity_curve(self, account_df):
        fig = Figure(figsize=(15, 10))
        ax1 = fig.add_subplot(111)

        # Ensure dates are properly formatted
        account_df["account_date"] = pd.to_datetime(account_df["account_date"])

        # Group by date and take the last entry for each day
        account_df = account_df.sort_values("account_date").groupby(account_df["account_date"].dt.date).last()

        # Convert back to datetime for plotting
        account_df.index = pd.to_datetime(account_df.index)

        # Extract x and y values
        x1 = account_df.index
        y1 = account_df["account_balance"]

        # Plot data
        ax1.plot(x1, y1, color="blue")
        ax1.set_title("Equity Curve")
        ax1.set_xlabel("")
        ax1.set_ylabel("Account Balance ($)")

        # Format x-axis with only available dates
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m-%Y"))
        ax1.set_xticks(x1)  # Ensure only available dates are shown

        # Rotate labels for better visibility
        for label in ax1.get_xticklabels():
            label.set_rotation(45)
            label.set_horizontalalignment("right")

        # Embed the Matplotlib figure in Tkinter
        self.canvas = FigureCanvasTkAgg(fig, master=self.parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

class RiskPage(BasePage):
    def __init__(self, username):
        super().__init__("Risk Page")
        self.username = username
        self.db = DatabaseManager()

        self.btblogo = self.load_image("assets/btblogo.png", (125, 150))
        tk.Button(self, image=self.btblogo, command = self.go_homepage, borderwidth=0, highlightthickness=0, highlightbackground="black", activebackground="black").place(anchor="nw")

        self.profilepic = self.load_image("assets/profile.png", (40, 40))
        tk.Label(self, text=username, image=self.profilepic, compound="left", font=("Arial", 30)).place(relx=1, rely=0, anchor="ne")

        self.btn_style = {"font": ("Arial", 30), "width": 12, "height": 2, "fg": "black", "bg": "black", "borderwidth": 2, "relief": "ridge"}
        self.selected_button = None

        tk.Label(self, text = "Select Risk Tolerance", font  = ("Arial", 50)).place(relx = 0.5, rely = 0.3, anchor = "center")
        self.btn1 = tk.Button(self, text="Level 1", **self.btn_style, command=lambda: self.level_clicked(self.btn1))
        self.btn2 = tk.Button(self, text="Level 2", **self.btn_style, command=lambda: self.level_clicked(self.btn2))
        self.btn3 = tk.Button(self, text="Level 3", **self.btn_style, command=lambda: self.level_clicked(self.btn3))

        # Place buttons
        self.btn1.place(relx=0.35, rely=0.5, anchor="center")
        self.btn2.place(relx=0.5, rely=0.5, anchor="center")
        self.btn3.place(relx=0.65, rely=0.5, anchor="center")


        

    def level_clicked(self, clicked_button):
        level_text = clicked_button.cget("text")
        if self.selected_button:
            self.selected_button.config(fg="black", relief="ridge")

        # Highlight the clicked button
        clicked_button.config(fg="green", relief="solid")

        # Update selected button reference
        self.selected_button = clicked_button
        
        self.selected_level = int(level_text[-1])
        print(self.selected_level)
        tk.Button(self, text="Confirm", font=("Arial", 30),command = self.apply_risk_thresholds, width=12, height=2, highlightbackground="green", bd=5, relief="solid").place(relx=0.5, rely=0.8, anchor="center")

    def apply_risk_thresholds(self):
        risk_level = int(self.selected_level)
        self.thresholds = self.db.get_risk_thresholds(risk_level)
        print(self.thresholds)
        self.navigate_to(WorkStationPage, self.username, risk_level, self.thresholds)
        self.destroy()

    def load_image(self, path, size):
        """function to load and resize an image."""
        img = Image.open(path)
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    def go_homepage(self):
        self.navigate_to(HomePage, self.username)
        self.destroy()

class WorkStationPage(BasePage):
    def __init__(self, username, risk_level, thresholds):
        super().__init__("WorkStation Page")
        self.username = username
        self.thresholds = thresholds
        self.risk_level = risk_level
        self.db = DatabaseManager()

        print("workstation page" , self.thresholds)

        self.btblogo = self.load_image("assets/btblogo.png", (125, 150))
        tk.Button(self, image=self.btblogo, command = self.go_homepage, borderwidth=0, highlightthickness=0, highlightbackground="black", activebackground="black").place(anchor="nw")

        self.profilepic = self.load_image("assets/profile.png", (40, 40))
        tk.Label(self, text=username, image=self.profilepic, compound="left", font=("Arial", 30)).place(relx=1, rely=0, anchor="ne")

        self.chart_frame = tk.Frame(self)
        self.chart_frame.place(relx=0.35, rely=0.55, anchor="center", width=1350, height=950)
        self.chart = BTCCandlestickChart(self.chart_frame)

        self.bi = BotIndicators(risk_level, thresholds)
        self.ab = ActivateBot(self, self.bi)
        while True:
            self.bi.calculate_rsi()
            self.bi.calculate_historical_rsi()
            self.bi.calculate_macd()
            self.bi.calculate_supertrend()
            print("rsi flag = ", self.bi.rsi_flag)
            print("macd flag = ", self.bi.macd_flag)
            print("supertrend flag = ", self.bi.st_flag)
            self.chart.plot_indicator_graphs(self.bi)
            self.update_price()
            self.display_indicators(self.bi)
            self.ab.buy_btc()
            if self.ab.buy_btc_price != 0:
                break
            time.sleep(10)
        
        while True:
            self.bi.calculate_rsi()
            self.bi.calculate_macd()
            self.bi.calculate_supertrend()
            print("rsi flag = ", self.bi.rsi_flag)
            print("macd flag = ", self.bi.macd_flag)
            print("supertrend flag = ", self.bi.st_flag)
            self.ab.sell_btc()
            if self.ab.sell_btc_price != 0:
                break
        

    def display_indicators(self, bi_class):
        """Fetch and update Bitcoin price every 5 seconds with proper placement."""
        price = BinanceAPI.get_ticker_price()
        
        if isinstance(price, float):
            price_text = f"Bitcoin Price: ${price:.2f}"
        else:
            price_text = price  # Show error if API fails

        # If label doesn't exist, create it
        if not hasattr(self, "price_label"):
            self.price_label = tk.Label(self, text=price_text, font=("Arial", 35), fg="white")
            self.price_label.place(relx=0.8, rely=0.2, anchor="center")
        else:
            self.price_label.config(text=price_text)

          

    def update_price(self):
        """Fetch and update Bitcoin price every 5 seconds with proper placement."""
        price = BinanceAPI.get_ticker_price()
        
        if isinstance(price, float):
            price_text = f"Bitcoin Price: ${price:.2f}"
        else:
            price_text = price  # Show error if API fails

        # If label doesn't exist, create it
        if not hasattr(self, "price_label"):
            self.price_label = tk.Label(self, text=price_text, font=("Arial", 35), fg="white")
            self.price_label.place(relx=0.825, rely=0.15, anchor="center")
        else:
            self.price_label.config(text=price_text)

        self.after(2000, self.update_price) 

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

    def load_image(self, path, size):
        """function to load and resize an image."""
        img = Image.open(path)
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    def go_homepage(self):
        self.navigate_to(HomePage, self.username)