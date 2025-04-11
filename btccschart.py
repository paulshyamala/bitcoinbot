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
    def __init__(self, parent, bi_class):
        """Initializes the candlestick chart inside the given Tkinter parent widget.
        
        Args:
            parent: The Tkinter parent widget where the chart will be embedded.
            bi_class: A class that holds the trading data and technical indicators.
        """
        self.parent = parent

    def get_ohlc_data(self, trading_preference, from_date, to_date):
        """Fetches the OHLC data for the specified date range.
        
        If trading_preference is 1, it fetches data for the last 30 days.
        
        Args:
            trading_preference: An integer indicating the preferred trading duration.
            from_date: The start date for fetching OHLC data.
            to_date: The end date for fetching OHLC data.
        """
        if trading_preference == 1:
            from_date = Utils.get_date() - timedelta(days=30)
            to_date = Utils.get_date()

        # Get OHLC data from Binance API
        self.ohlc_data = BinanceAPI.get_ohlc_day_range(from_date, to_date)

    def plot_indicator_graphs(self, bi_class):
        """Plots RSI, MACD, Supertrend, and Prices in a 2x2 Matplotlib figure inside Tkinter without explicitly passing X values.
        
        Args:
            bi_class: A class that contains the necessary data for plotting the indicators.
        """
        # Create a Matplotlib Figure with 2x2 subplots
        fig = Figure(figsize=(12, 8))
        ax1 = fig.add_subplot(221)  # RSI
        ax2 = fig.add_subplot(222)  # MACD
        ax3 = fig.add_subplot(223)  # Supertrend
        ax4 = fig.add_subplot(224)  # Prices

        # Adjust subplot spacing
        fig.subplots_adjust(hspace=0.4,  wspace=0.3)

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
        

        # Plot Supertrend
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
        self.plot_candlestick_chart(fig, ax1)  # Call to plot the candlestick chart
        self.canvas.draw()  # Draw the canvas
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_candlestick_chart(self, fig, ax):
        """Plots the BTC/USDT candlestick chart inside Tkinter.
        
        Args:
            fig: The Matplotlib figure object.
            ax: The axis object where the candlestick chart will be plotted.
        """
        self.fig = fig
        self.ax = ax

        # Bind Mouse Hover Event to handle tooltip
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

        # Format x-axis for dates
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))  # Date format
        self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))  # X-axis tick interval
        for label in self.ax.get_xticklabels():
            label.set_rotation(45)  # Rotate labels for better readability
            label.set_horizontalalignment('right')

        # Plot each candlestick (OHLC) data
        for x, o, h, l, c in self.ohlc_data:
            color = 'g' if c >= o else 'r'  # Green for bullish, red for bearish candlesticks
            self.ax.plot([x, x], [l, h], color=color)  # Wick (line between high and low)
            self.ax.add_patch(Rectangle((x - 0.3, min(o, c)), 0.6, abs(o - c), color=color))  # Body of the candlestick

        # Annotation for OHLC tooltip
        self.ohlc_annot = self.ax.annotate("", xy=(0, 0), xytext=(-50, 50), textcoords="offset points",
                                           bbox=dict(boxstyle="round", fc="w"),
                                           arrowprops=dict(arrowstyle="->"))
        self.ohlc_annot.set_visible(False)

        # Set the title and labels for the chart
        self.ax.set_title("BTC/USDT")
        self.ax.set_ylabel("Price($)")

    def is_cursor_on_candlestick(self, event):
        """Checks if the cursor is over a candlestick body.
        
        Args:
            event: The event object generated when the user hovers the cursor.
        
        Returns:
            int: The index of the candlestick if hovered, None otherwise.
        """
        for i, (x, o, h, l, c) in enumerate(self.ohlc_data):
            if abs(x - event.xdata) < 0.3 and l <= event.ydata <= h:
                return i
        return None

    def update_ohlc_annot(self, index):
        """Updates the OHLC tooltip when hovering over a candlestick.
        
        Args:
            index: The index of the candlestick being hovered.
        """
        x, o, h, l, c = self.ohlc_data[index]
        self.ohlc_annot.xy = (x, c)  # Set the position of the annotation
        text = f"Date: {mdates.num2date(x).strftime('%b %d')}\nOpen: {o}\nHigh: {h}\nLow: {l}\nClose: {c}"
        self.ohlc_annot.set_text(text)  # Set the text of the tooltip
        self.ohlc_annot.get_bbox_patch().set_alpha(0.9)  # Set tooltip transparency

    def on_hover(self, event):
        """Handles the hover event for showing tooltips when hovering over candlesticks.
        
        Args:
            event: The event object generated when the user hovers the cursor.
        """
        if event.inaxes == self.ax:
            candlestick_index = self.is_cursor_on_candlestick(event)  # Check if hovering over a candlestick
            if candlestick_index is not None:
                self.update_ohlc_annot(candlestick_index)  # Update tooltip with OHLC data
                self.ohlc_annot.set_visible(True)  # Make tooltip visible
            else:
                self.ohlc_annot.set_visible(False)  # Hide tooltip if not hovering over a candlestick

            self.canvas.draw_idle()  # Update the canvas to refresh the tooltip
        else:
            self.ohlc_annot.set_visible(False)  # Hide tooltip when not hovering over the chart
            self.canvas.draw_idle()  # Update the canvas
