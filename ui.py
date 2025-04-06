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
from datetime import datetime, timedelta
from utils import Utils

class DisplayPictures:
    @staticmethod
    def load_image(page_obj, username, page_heading):
        """function to load and resize an image."""
        img = Image.open("assets/btblogo.png")
        img = img.resize((125, 150), Image.LANCZOS)
        page_obj.btblogo = ImageTk.PhotoImage(img)
        tk.Button(page_obj, image=page_obj.btblogo, command = page_obj.go_homepage, borderwidth=0, highlightthickness=0, highlightbackground="black", activebackground="black").place(anchor="nw")

        img = Image.open("assets/profile.png")
        img = img.resize((40, 40), Image.LANCZOS)
        page_obj.profilepic = ImageTk.PhotoImage(img)
        tk.Label(page_obj, text=username, image=page_obj.profilepic, compound="left", font=("Arial", 30)).place(relx=1, rely=0, anchor="ne")

        tk.Label(page_obj, text = page_heading, font = ("Arial", 60)).place(relx = 0.5, rely = 0.1, anchor = "center")

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
        self.username_entry.insert(0, "charlie1")
        tk.Button(self, text="?", font=("Arial", 15), command=self.show_username_rules).place(relx = 0.35, rely= 0.09)


        tk.Label(self, text="Password:", **btn_style).pack(pady=5)
        self.password_entry = tk.Entry(self, show="*", bd=5, font=("Arial", 30), width=20)
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "Harper1#")
        tk.Button(self, text="?", font=("Arial", 15), command=self.show_password_rules).place(relx = 0.35, rely= 0.23)

        tk.Button(self, text="Login", **btn_style, 
                  command=self.handle_login).place(relx=0.5, rely=0.5, anchor="center")

        tk.Button(self, text="Register", **btn_style, 
                  command=self.handle_register).place(relx=0.5, rely=0.6, anchor="center")
        self.status_label = tk.Label(self, text="")
        self.status_label.pack(pady=5)

    def show_username_rules(self):
        self._create_popup("Username Rules", [
            "• The first letter should be an alphabet",
            "• Username should be 8-12 characters long",
            "• No special characters allowed"
        ])

    def show_password_rules(self):
        self._create_popup("Password Rules", [
            "• At least 1 capital letter",
            "• At least 1 number",
            "• At least 1 special character",
            "• Minimum 8 characters"
        ])

    def _create_popup(self, title, rules):
        popup = tk.Toplevel(self)
        popup.title(title)
        popup.geometry("400x200")
        popup.transient(self)  # keeps popup on top
        popup.resizable(False, False)
        tk.Label(popup, text=title, font=("Arial", 18, "bold")).pack(pady=10)

        for rule in rules:
            tk.Label(popup, text=rule, font=("Arial", 12)).pack(anchor="w", padx=20)

        tk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)
        
    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        message = self.auth.validate_login(username, password)
        self.status_label.config(text=message)

        if message == "Login Successful":
            self.auth.close()
            self.navigate_to(PreferencePage, username)

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

class PreferencePage(BasePage):
    def __init__(self, username):
        super().__init__("Account Page")
        self.username = username

        DisplayPictures.load_image(self, username, "Select Trading Preference")

        self.btn_style = {"font": ("Arial", 30), "width": 12, "height": 2, "fg": "black", "bg": "white", "borderwidth": 2, "relief": "ridge"}
        self.selected_button = None
        
        self.btn1 = tk.Button(self, text="Live Trading", **self.btn_style, command=lambda: self.level_clicked(self.btn1))
        self.btn2 = tk.Button(self, text="Historical Trading", **self.btn_style, command=lambda: self.level_clicked(self.btn2))

        # Place buttons
        self.btn1.place(relx=0.40, rely=0.5, anchor="center")
        self.btn2.place(relx=0.6, rely=0.5, anchor="center")
    
    def level_clicked(self, clicked_button):
        button_text = clicked_button.cget("text")
        if self.selected_button:
            self.selected_button.config(fg="black", relief="ridge")

        # Highlight the clicked button
        clicked_button.config(fg="green", relief="solid")

        # Update selected button reference
        self.selected_button = clicked_button
        print(button_text)
        if button_text == "Live Trading":
            trading_preference = 1
        else:
            trading_preference = 0

        
        confirm_button = tk.Button(self, text="Confirm", font=("Arial", 30),command =lambda: self.go_homepage(trading_preference), width=12, height=2, highlightbackground="green", bd=5, relief="solid")
        confirm_button.place(relx=0.50, rely=0.8, anchor="center")
      
    
    def go_homepage(self, trading_preference):
        print("Selected preference:", trading_preference)
        self.trading_preference = trading_preference
        self.db = DatabaseManager(trading_preference)
        self.navigate_to(HomePage, self)
        self.destroy()

class AccountPage(BasePage):
    def __init__(self, user_obj):
        super().__init__("Account Page")
        self.user_obj = user_obj

       
        DisplayPictures.load_image(self, user_obj.username, "Balance Update")

       
        tk.Label(self, text="How much money do you want to put in?", font=("Arial", 30)).place(relx=0.5, rely=0.4, anchor="center")

        self.accountbalance_entry = tk.Entry(self, bd=5, font=("Arial", 30), width=20)
        self.accountbalance_entry.place(relx=0.6, rely=0.5, anchor="center")

        btn_style = {"font": ("Arial", 30), "width": 12, "height": 2}
        tk.Label(self, text="Balance ($)", font=("Arial", 30), bd=5, relief="solid").place(relx=0.35, rely=0.5, anchor="center")

        tk.Button(self, text="Confirm", **btn_style, 
                  command=self.add_balance).place(relx=0.5, rely=0.6, anchor="center")

    def go_homepage(self):
        self.navigate_to(HomePage, self.user_obj)
        self.destroy()

    def add_balance(self):
        """Calls DatabaseManager to update the database with balance."""
        try:
            balance = float(self.accountbalance_entry.get())
            success, new_balance = self.user_obj.db.update_account_balance(self.user_obj.username, balance)
            if success:
                messagebox.showinfo("Success", f"Balance updated: ${new_balance:.2f}")
               
                self.navigate_to(HomePage, self.user_obj)
                self.destroy()
                  # Close the window after confirmation

            else:
                messagebox.showerror("Error", "Failed to update balance. Account Balance should be between 500$ and 5000$")
        except ValueError:
            messagebox.showerror("Error", "Invalid input! Please enter a valid number.")

    def on_close(self):
        self.destroy()

class HomePage(BasePage):
    def __init__(self, user_obj):
        super().__init__("Home Page")
        self.user_obj = user_obj

        # self.btblogo = self.load_image("assets/btblogo.png", (125, 150))
        # tk.Label(self, image=self.btblogo).place(anchor="nw")

        # self.profilepic = self.load_image("assets/profile.png", (40, 40))
        # tk.Label(self, text=self.user_obj.username, image=self.profilepic, compound="left", font=("Arial", 30)).place(relx=1, rely=0, anchor="ne")

        DisplayPictures.load_image(self, user_obj.username,"Home")      
       # tk.Button(self, image=self.btblogo, command = self.go_homepage, borderwidth=0, highlightthickness=0, highlightbackground="black", activebackground="black").place(anchor="nw")

        btn_style = {"font": ("Arial", 30), "width": 12, "height": 2}

        
        tk.Button(self, text="Profile", **btn_style, command = self.profile).place(relx=0.35, rely=0.5, anchor= "center")
        tk.Button(self, text="Add Money", **btn_style, command = self.add_money).place(relx=0.5, rely=0.5, anchor="center")
        tk.Button(self, text="Trade History", **btn_style, command = self.trade_history).place(relx=0.65, rely=0.5, anchor="center")
        tk.Button(self, text="Start Trading", font=("Arial", 30), command = self.start_trading, width=12, height=2, highlightbackground="green", bd=5, relief="solid").place(relx=0.5, rely=0.8, anchor="center")

   
    
    def go_homepage(self):
        self.navigate_to(HomePage, self.user_obj)
        self.destroy()
    
    def profile(self):
        self.navigate_to(ProfilePage, self.user_obj)
        

    def add_money(self):
        self.navigate_to(AccountPage, self.user_obj)
        self.destroy()

    def trade_history(self):
        self.navigate_to(TradeHistoryPage, self.user_obj)
        self.destroy()

    def start_trading(self):
        print("start trading page ", self.user_obj.trading_preference)
        if self.user_obj.trading_preference == 0:
            self.navigate_to(DatePage, self.user_obj)
        else:
            self.navigate_to(RiskPage, self.user_obj)
        self.destroy()

class DatePage(BasePage):
    def __init__(self, user_obj):
        super().__init__("Account Page")
        self.user_obj = user_obj

        DisplayPictures.load_image(self, user_obj.username,"Enter Date Range")

       

        btn_style = {"font": ("Arial", 30), "width": 12, "height": 2}

        tk.Label(self, text="From Date:", **btn_style).place(relx = 0.3, rely = 0.3)
        self.from_date_entry = tk.Entry(self, bd=5, font=("Arial", 30), width=20)
        self.from_date_entry.place(relx = 0.3, rely = 0.4)
        self.from_date_entry.insert(0, "2024-01-01")

        tk.Label(self, text="To Date:", **btn_style).place(relx = 0.5, rely = 0.3)
        self.to_date_entry = tk.Entry(self, bd=5, font=("Arial", 30), width=20)
        self.to_date_entry.place(relx = 0.5, rely = 0.4)
        self.to_date_entry.insert(0, "2024-02-01")
        #Save in self.user_obj.fron_date , to_date

        tk.Button(self, text="Confirm", **btn_style, command=self.handle_date_entry).place(relx=0.5, rely=0.8, anchor="center")
    
    def handle_date_entry(self):
        from_date = self.from_date_entry.get()
        to_date = self.to_date_entry.get()
        try:
            from_ts = datetime.strptime(from_date, "%Y-%m-%d")
            to_ts = datetime.strptime(to_date, "%Y-%m-%d")
            # if (to_ts < from_ts) or (to_ts > Utils.get_date()):
            #     print("Invalid Input try")
            #     print("historical trading", from_ts, to_ts)
            #     messagebox.showerror("Error", "Invalid Input. Please enter in the required format")
            # else:
            self.user_obj.from_date = from_ts
            self.user_obj.to_date = to_ts
            print("historical trading", from_ts, to_ts)
            self.go_riskpage()
        except:
            print("Invalid input except", from_ts, to_ts)
            messagebox.showerror("Error", "Invalid Input. Please enter in the required format")
            
        
        
        

    def go_homepage(self):
        self.navigate_to(HomePage, self.user_obj)
        self.destroy()
    
    def go_riskpage(self):
        self.navigate_to(RiskPage, self.user_obj)
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
    def __init__(self, user_obj):
        super().__init__("Trade History Page")
        self.user_obj = user_obj

        DisplayPictures.load_image(self,user_obj.username,"Trade History")
        

        btn_style = {"font": ("Arial", 30), "width": 12, "height": 2}
        trade_df = self.user_obj.db.get_trade_history(self.user_obj.username)
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

        root =  ttk.Frame(self)
        root.place(relx=0.0015, rely=0.15, relwidth=0.98, relheight=0.75)

        self.create_table(root, df_buy, "Buy Transactions")
        self.create_table(root, df_sell, "Sell Transactions")
    
    def go_homepage(self):
        self.navigate_to(HomePage, self.user_obj)
        self.destroy()

class ProfilePage(BasePage):
    def __init__(self, user_obj):
        super().__init__("Profile Page")
        self.user_obj = user_obj
        account_valid, account_df = self.user_obj.db.get_account_history(self.user_obj.username)
        root =  ttk.Frame(self)
        #root.pack(fill=tk.BOTH, expand=True, padx=20, pady=10) 
        # root.place(relx=0.0015, rely=0.15, width=self.winfo_width(), height=self.winfo_height()) 
        root.place(relx=0.0015, rely=0.15, relwidth=0.5, relheight=0.7)
        self.parent = root

        DisplayPictures.load_image(self,user_obj.username, "Profile")      
       
        tk.Label(self, text="Account Balance", font=("Arial", 30)).place(relx=0.8, rely=0.4, anchor="center")

        

        account_balance = round(self.user_obj.db.get_account_balance(self.user_obj.username), 2)
        tk.Label(self, text=f"{account_balance} $", font=("Arial", 30)).place(relx=0.8, rely=0.5, anchor="center")
        if account_valid == True:
            self.plot_equity_curve(account_df)
        else:
            print("No history available")

    def go_homepage(self):
        self.navigate_to(HomePage, self.user_obj)
        self.destroy()

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

class BotIndicatorsPage(BasePage):
    def __init__(self, user_obj):
        super().__init__("Bot Indicators Page")
        self.user_obj = user_obj

        print("Bot Indicators Page" , self.user_obj.thresholds)

        DisplayPictures.load_image(self, user_obj.username,"Bot Indicators")
        
        self.chart_frame = tk.Frame(self)
        self.chart_frame.place(relx=0.5, rely=0.55, anchor="center", width=1350, height=800)
        

        self.bi = BotIndicators(self.user_obj)
        self.chart = BTCCandlestickChart(self.chart_frame, self.bi)
        self.ab = ActivateBot(user_obj, self, self.bi)
        to_date = self.bi.to_date

        if self.user_obj.trading_preference == 1:
            to_date = Utils.get_date()

        self.bi.calculate_macd(to_date)
        self.bi.calculate_supertrend(to_date)
        self.bi.calculate_historical_rsi(to_date)
        
        self.chart.get_ohlc_data(self.user_obj.trading_preference, self.user_obj.from_date, self.user_obj.to_date)
        print("historical rsi done")
        self.chart.plot_indicator_graphs(self.bi)

    def go_homepage(self):
        self.navigate_to(HomePage, self.user_obj)

class RiskPage(BasePage):
    def __init__(self, user_obj):
        super().__init__("Risk Page")
        self.user_obj = user_obj
        print("risk page ", self.user_obj.trading_preference)

        DisplayPictures.load_image(self, user_obj.username,"Risk Levels")
        
        self.btn_style = {"font": ("Arial", 30), "width": 12, "height": 2, "fg": "black", "bg": "white", "borderwidth": 2, "relief": "ridge"}
        self.selected_button = None

        tk.Label(self, text = "Note: Risk Increases from 1 to 3", font  = ("Arial", 50)).place(relx = 0.5, rely = 0.3, anchor = "center")
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
        print("risk level:" , self.selected_level)
        tk.Button(self, text="Activate Bot", font=("Arial", 30),command = self.apply_risk_thresholds, width=12, height=2, highlightbackground="green", bd=5, relief="solid").place(relx=0.40, rely=0.8, anchor="center")
        tk.Button(self, text="Indicator Graphs", font=("Arial", 30),command = self.bot_indicators, width=12, height=2, highlightbackground="green", bd=5, relief="solid").place(relx=0.6, rely=0.8, anchor="center")

    def apply_risk_thresholds(self):
        self.user_obj.risk_level = int(self.selected_level)
        self.user_obj.thresholds = self.user_obj.db.get_risk_thresholds(self.user_obj.risk_level)
        print(self.user_obj.thresholds)
        self.navigate_to(WorkStationPage, self.user_obj)
        self.destroy()
    
    def bot_indicators(self):
        self.user_obj.risk_level = int(self.selected_level)
        self.user_obj.thresholds = self.user_obj.db.get_risk_thresholds(self.user_obj.risk_level)
        self.navigate_to(BotIndicatorsPage, self.user_obj)
        self.destroy()

    def go_homepage(self):
        self.navigate_to(HomePage, self.user_obj)
        self.destroy()

class WorkStationPage(BasePage):

    def __init__(self, user_obj):
        super().__init__("WorkStation Page")
        self.user_obj = user_obj

        print("workstation page" , self.user_obj.thresholds)

        DisplayPictures.load_image(self, user_obj.username,"WorkStation")
        

        self.chart_frame = tk.Frame(self)
        self.chart_frame.place(relx=0.3, rely=0.55, anchor="center" ,width=1200, height=800)
        self.bi = BotIndicators(user_obj)
        self.chart = BTCCandlestickChart(self.chart_frame, self.bi)
        self.ab = ActivateBot(user_obj, self, self.bi)
        self.from_date = self.bi.from_date
        self.to_date = self.bi.to_date
        self.running_buy = True
        self.after(1000, self.run_buy_loop)

        self.chart.get_ohlc_data(self.user_obj.trading_preference, self.user_obj.from_date, self.user_obj.to_date)

    def run_buy_loop(self):
        if (self.bi.continuous_trade):
            if (not self.running_buy):
                return
        else:
            if self.from_date > self.to_date  or not self.running_buy:
                return  # End loop if done

        print('buy activated for this date: ', self.from_date)
        print("btc value: ", BinanceAPI.get_price_on_day(self.from_date))

        self.bi.calculate_rsi(self.from_date)
        self.bi.calculate_macd(self.from_date)
        self.bi.calculate_supertrend(self.from_date)
        if self.user_obj.trading_preference == 1:
            self.chart.get_ohlc_data(self.user_obj.trading_preference, self.user_obj.from_date, self.user_obj.to_date)

        print("rsi flag = ", self.bi.rsi_flag)
        print("macd flag = ", self.bi.macd_flag)
        print("supertrend flag = ", self.bi.st_flag)


        self.ab.buy_btc(self.from_date)

        self.display_indicators()
        if self.ab.buy_btc_price != 0:
            self.running_buy = False
            self.after(1000, self.run_sell_loop)  # Start selling loop
            return
        if self.bi.continuous_trade:
            self.from_date = Utils.get_date()
            self.after(60000, self.run_buy_loop)  # Repeat in 1 second
        else:
            self.from_date += timedelta(days=1)
            self.after(1000, self.run_buy_loop)  # Repeat in 1 second

    def run_display_loop(self):
        self.display_indicators()
        self.after(2000, self.run_display_loop)

    def run_sell_loop(self):
        if not self.bi.continuous_trade and self.from_date > self.to_date:
            return  # Done

        print('sell activated for this date: ', self.from_date)
        print("btc value: ", BinanceAPI.get_price_on_day(self.from_date))

        self.bi.calculate_rsi(self.from_date)
        self.bi.calculate_macd(self.from_date)
        self.bi.calculate_supertrend(self.from_date)
        if self.user_obj.trading_preference == 1:
            self.chart.get_ohlc_data(self.user_obj.trading_preference, self.user_obj.from_date, self.user_obj.to_date)

        print("rsi flag = ", self.bi.rsi_flag)
        print("macd flag = ", self.bi.macd_flag)
        print("supertrend flag = ", self.bi.st_flag)

        self.ab.sell_btc(self.from_date)
        self.display_indicators()
        if self.ab.sell_btc_price != 0:
            self.run_display_loop()
            return  # Sell done
        
        if self.bi.continuous_trade:
            self.from_date = Utils.get_date()
            self.after(60000, self.run_sell_loop)  # Repeat in 1 second
        else:
            self.from_date += timedelta(days=1)
            self.after(1000, self.run_sell_loop)


    def display_indicators(self):
        """Fetch and update Bitcoin price every 5 seconds with proper placement."""
        price = BinanceAPI.get_ticker_price()
        
        if isinstance(price, float):
            price_text = f"Bitcoin Price: ${price:.2f}"
        else:
            price_text = price  # Show error if API fails

        # If label doesn't exist, create it
        if not hasattr(self, "price_label"):
            self.price_label = tk.Label(self, text=price_text, font=("Arial", 35), fg="black")
            self.price_label.place(relx=0.8, rely=0.2, anchor="center")
        else:
            self.price_label.config(text=price_text)
        
        fig = Figure(figsize=(16, 10))
        ax = fig.add_subplot(111)  
        self.chart.canvas = FigureCanvasTkAgg(fig, master=self.chart.parent)
        self.chart.plot_candlestick_chart(fig,ax)
        self.chart.canvas.draw()
        self.chart.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


        self.truepic = self.load_image("assets/true.png", (30, 30))
        

        self.falsepic = self.load_image("assets/false.png", (30, 30))
     

        tk.Label(self, text=f"Date: {self.from_date}", font=("Arial", 25), fg="black").place(relx=0.8, rely=0.16, anchor="center")
        if self.running_buy:
            tk.Label(self, text="BUY Mode", font=("Arial", 25), fg="black").place(relx=0.8, rely=0.25, anchor="center")
            rsi_flag = False
            macd_flag = False
            st_flag = False
            if self.bi.rsi_flag ==1 :
                rsi_flag = True
            if self.bi.macd_flag ==1 :
                macd_flag = True
            if self.bi.st_flag ==1 :
                st_flag = True
        else:
            tk.Label(self, text="Sell Mode", font=("Arial", 25), fg="black").place(relx=0.8, rely=0.25, anchor="center")
            rsi_flag = False
            macd_flag = False
            st_flag = False
            if self.bi.rsi_flag ==-1 :
                rsi_flag = True
            if self.bi.macd_flag ==-1 :
                macd_flag = True
            if self.bi.st_flag ==-1 :
                st_flag = True

        if rsi_flag == True:

            tk.Label(self, text="RSI Flag: ", image=self.truepic, compound = "right", font=("Arial", 25), fg="black").place(relx=0.8, rely=0.3, anchor="center")
        else:
            tk.Label(self, text="RSI Flag: ", image=self.falsepic, compound ="right",  font=("Arial", 25), fg="black").place(relx=0.8, rely=0.3, anchor="center")

        if macd_flag == True:

            tk.Label(self, text="MACD Flag: ", image=self.truepic, compound = "right", font=("Arial", 25), fg="black").place(relx=0.8, rely=0.4, anchor="center")
        else:
            tk.Label(self, text="MACD Flag: ", image=self.falsepic, compound ="right",  font=("Arial", 25), fg="black").place(relx=0.8, rely=0.4, anchor="center")
        
        if st_flag == True:

            tk.Label(self, text="Supertrend Flag: ", image=self.truepic, compound = "right", font=("Arial", 25), fg="black").place(relx=0.8, rely=0.5, anchor="center")
        else:
            tk.Label(self, text="Supertrend Flag: ", image=self.falsepic, compound ="right",  font=("Arial", 25), fg="black").place(relx=0.8, rely=0.5, anchor="center")


        if not hasattr(self.ab, "trading_amount"):
            tk.Label(self, text="Amount Bought: No data yet", font=("Arial", 25), fg="black").place(relx=0.8, rely=0.6, anchor="center")
        else:
            tk.Label(self, text=f"Amount Bought: {round(self.ab.trading_amount, 2)}$ ", font=("Arial", 25), fg="black").place(relx=0.8, rely=0.6, anchor="center")
        
        if not hasattr(self.ab, "buy_btc_price"):
            tk.Label(self, text="Bought At: No data yet", font=("Arial", 25), fg="black").place(relx=0.8, rely=0.7, anchor="center")
        else:
            tk.Label(self, text=f"Bought At: {round(self.ab.buy_btc_price, 2)}$ ", font=("Arial", 25), fg="black").place(relx=0.8, rely=0.7, anchor="center")
        
        if not hasattr(self.ab, "sell_btc_price"):
            tk.Label(self, text="Sold At: No data yet", font=("Arial", 25), fg="black").place(relx=0.8, rely=0.8, anchor="center")
        else:
            tk.Label(self, text=f"Sold At: {round(self.ab.sell_btc_price, 2)}$ ", font=("Arial", 25), fg="black").place(relx=0.8, rely=0.8, anchor="center")

        if not hasattr(self.ab, "profit_loss"):
            tk.Label(self, text="Profit/Loss: No data yet", font=("Arial", 25), fg="black").place(relx=0.8, rely=0.9, anchor="center")
        else:
            tk.Label(self, text=f"Profit/Loss: {round(self.ab.profit_loss, 2)}$ ", font=("Arial", 25), fg="black").place(relx=0.8, rely=0.9, anchor="center")

          

    def update_price(self):
        """Fetch and update Bitcoin price every 5 seconds with proper placement."""
        price = BinanceAPI.get_ticker_price()
        
        if isinstance(price, float):
            price_text = f"Bitcoin Price: ${price:.2f}"
        else:
            price_text = price  # Show error if API fails

        # If label doesn't exist, create it
        if not hasattr(self, "price_label"):
            self.price_label = tk.Label(self, text=price_text, font=("Arial", 35), fg="black")
            self.price_label.place(relx=0.825, rely=0.15, anchor="center")
        else:
            self.price_label.config(text=price_text)

        self.after(2000, self.update_price) 

    def go_homepage(self):
        self.navigate_to(HomePage, self.user_obj)
        self.destroy()

