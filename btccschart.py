import requests
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from api import BinanceAPI
from utils import Utils
from datetime import datetime, timedelta

class BTCCandlestickChart:
    def __init__(self, parent):
        """Initializes the candlestick chart inside the given Tkinter parent widget."""
        self.parent = parent

        current_date = Utils.get_date()
        from_date = current_date - timedelta(days=30)
        self.ohlc_data = BinanceAPI.get_ohlc_day_range(from_date, current_date)


    def plot_indicator_graphs(self, bi_class):
        """Plot RSI, MACD, Supertrend, and Prices in a 2x2 Matplotlib figure inside Tkinter without explicitly passing X values."""

        # Create a Matplotlib Figure with 2x2 subplots
        fig = Figure(figsize=(12, 6))
        ax1 = fig.add_subplot(221)  # RSI
        ax2 = fig.add_subplot(222)  # MACD
        ax3 = fig.add_subplot(223)  # Supertrend
        ax4 = fig.add_subplot(224)  # Prices

        # Extract data from bi_class
        y1 = bi_class.rsi_values  # RSI values
        y21 = bi_class.macd_line_filtered  # MACD line
        y22 = bi_class.signal_line_filtered  # Signal line
        y31 = bi_class.supertrend_green  # Supertrend Buy
        y32 = bi_class.supertrend_prices  # Supertrend Prices
        y33 = bi_class.supertrend_red  # Supertrend Sell

        # 🚀 No need to pass x values! Matplotlib automatically uses index positions

        # Plot RSI
        x1 = list(range(len(y1)))
        ax4.plot(x1, y1, color="blue")
        ax4.set_title("RSI - 100 Days")
        ax4.set_xlabel("Days")
        ax4.set_ylabel("Percentage")

        # Plot MACD & Signal Line
        ax2.plot(y21, color="purple", label="MACD Line")
        ax2.plot(y22, color="pink", label="Signal Line")
        ax2.set_title("MACD - 100 Days")
        ax2.legend()
        ax2.set_xlabel("Days")
        

        # Plot Supertrend\
       
        ax3.plot(y31, label="Buy Signal", color="green")
        ax3.plot(y32, label="Price", color="blue")
        ax3.plot(y33, label="Sell Signal", color="red")
        ax3.set_title("Supertrend - 100 Days")
        ax3.legend()
        ax3.set_xlabel("Days")
        ax3.set_ylabel("Price($)")
        
        # Plot Prices
        # x4 = list(range(len(y32)))
        # ax4.plot(x4, y32, color="purple")
        # ax4.set_title("Prices")

        # # Hide X-Axis
        # for ax in [ ax2, ax3]:
        #     ax.set_xticks([])  # Remove tick marks
        #     ax.set_xticklabels([])  # Remove tick labels
        #     ax.set_xlabel('')  # Remove axis label
        #     ax.spines['bottom'].set_visible(False)  # Hide x-axis line

        # Embed the Matplotlib figure in Tkinter
        self.canvas = FigureCanvasTkAgg(fig, master=self.parent)
        self.plot_candlestick_chart(fig,ax1)
        # self.ax.grid()
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)



    # def get_btc_ohlc(self):
    #     """Fetches the last 30 days of BTC/USDT OHLC data from Binance API."""
    #     url = "https://api.binance.com/api/v3/klines"
    #     params = {"symbol": "BTCUSDT", "interval": "1d", "limit": 30}
    #     response = requests.get(url, params=params).json()

    #     ohlc_data = []
    #     for candle in response:
    #         timestamp = datetime.datetime.fromtimestamp(candle[0] / 1000)
    #         ohlc_data.append([
    #             mdates.date2num(timestamp),
    #             float(candle[1]),  # Open
    #             float(candle[2]),  # High
    #             float(candle[3]),  # Low
    #             float(candle[4])   # Close
    #         ])
    #     return ohlc_data

    def plot_candlestick_chart(self, fig, ax):
        """Plots the BTC/USDT candlestick chart inside Tkinter."""
        self.fig = fig
        self.ax = ax



        # Bind Mouse Hover Event
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

        # Format x-axis for dates
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        for label in self.ax.get_xticklabels():
            label.set_rotation(45)
            label.set_horizontalalignment('right')


        for x, o, h, l, c in self.ohlc_data:
            color = 'g' if c >= o else 'r'
            self.ax.plot([x, x], [l, h], color=color)  # Wick
            self.ax.add_patch(Rectangle((x - 0.3, min(o, c)), 0.6, abs(o - c), color=color))

        # Annotation for OHLC tooltip
        self.ohlc_annot = self.ax.annotate("", xy=(0, 0), xytext=(-50, 50), textcoords="offset points",
                                           bbox=dict(boxstyle="round", fc="w"),
                                           arrowprops=dict(arrowstyle="->"))
        self.ohlc_annot.set_visible(False)

        self.ax.set_title("BTC/USDT")
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Price($)")
        # self.ax.grid()
        # self.canvas.draw()

    def is_cursor_on_candlestick(self, event):
        """Checks if the cursor is over a candlestick body."""
        for i, (x, o, h, l, c) in enumerate(self.ohlc_data):
            if abs(x - event.xdata) < 0.3 and l <= event.ydata <= h:
                return i
        return None

    def update_ohlc_annot(self, index):
        """Updates the OHLC tooltip when hovering over a candlestick."""
        x, o, h, l, c = self.ohlc_data[index]
        self.ohlc_annot.xy = (x, c)
        text = f"Date: {mdates.num2date(x).strftime('%b %d')}\nOpen: {o}\nHigh: {h}\nLow: {l}\nClose: {c}"
        self.ohlc_annot.set_text(text)
        self.ohlc_annot.get_bbox_patch().set_alpha(0.9)

    def on_hover(self, event):
        """Handles the hover event for showing tooltips."""
        if event.inaxes == self.ax:
            candlestick_index = self.is_cursor_on_candlestick(event)
            if candlestick_index is not None:
                self.update_ohlc_annot(candlestick_index)
                self.ohlc_annot.set_visible(True)
            else:
                self.ohlc_annot.set_visible(False)

            self.canvas.draw_idle()
        else:
            self.ohlc_annot.set_visible(False)
            self.canvas.draw_idle()

