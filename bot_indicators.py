import requests
from api import BinanceAPI
from datetime import datetime
from datetime import datetime, timedelta

class BotIndicators:
    def __init__(self, risk_level, thresholds):
        self.symbol = "BTCUSDT"
        self.prices = None  # Stores fetched prices to avoid redundant API calls
        self.highs, self.lows, self.prices = None, None, None
        self.thresholds = self.get_risk_thresholds(thresholds)
        self.risk_level = risk_level
        self.from_date = datetime.strptime('2024-11-05', "%Y-%m-%d")
        self.to_date = datetime.strptime('2024-12-05', "%Y-%m-%d")

    def get_risk_thresholds(self, thresholds):

    
        return {
            "invest_thres": thresholds["invest_thres"][0],
            "rsi_oversold": thresholds["rsi_oversold"][0],
            "rsi_overbought": thresholds["rsi_overbought"][0],
            "macd_fast_ema": thresholds["macd_fast_ema"][0],
            "macd_slow_ema": thresholds["macd_slow_ema"][0],
            "macd_signal_ema": thresholds["macd_signal_ema"][0],
            "supertrend_atr_period": thresholds["supertrend_atr_period"][0],
            "supertrend_multiplier": thresholds["supertrend_multiplier"][0]
        }
   
    # def get_prices(self, period):
    #     """Fetches closing prices from Binance API based on the given period."""
    #     url = "https://api.binance.com/api/v3/klines"
    #     params = {"symbol": self.symbol, "interval": "1d", "limit": period}
    #     response = requests.get(url, params=params).json()

    #     self.prices = [float(candle[4]) for candle in response]  # Store closing prices
    #     self.highs = [float(candle[2]) for candle in response]  # Extract High prices
    #     self.lows = [float(candle[3]) for candle in response]  # Extract Low prices
    #     return


    def calculate_rsi(self, given_date):
        """Calculates and returns the RSI along with its status."""
        period = 14
        #BinanceAPI.get_prices(self, period + 1)  # Fetch prices only if not already fetched
        from_date = given_date - timedelta(days=period+1)
        to_date = given_date 
        BinanceAPI.get_prices_day_range(self, from_date, to_date)
        gains, losses = [], []

        # Compute initial gains and losses
        for i in range(1, period + 1):
            change = self.prices[i] - self.prices[i - 1]
            gains.append(max(change, 0))
            losses.append(abs(min(change, 0)))

        # Compute initial average gain and loss
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        # Compute RSI for the most recent price
        change = self.prices[-1] - self.prices[-2]
        gain = max(change, 0)
        loss = abs(min(change, 0))

        # Calculate smoothed averages
        avg_gain = ((avg_gain * (period - 1)) + gain) / period
        avg_loss = ((avg_loss * (period - 1)) + loss) / period

        # Compute RSI
        rs = avg_gain / avg_loss if avg_loss != 0 else 100  # Prevent division by zero
        self.rsi = 100 - (100 / (1 + rs))
        #print("RSI ", self.rsi, self.thresholds["rsi_overbought"], self.thresholds["rsi_oversold"])
         # Determine RSI status
        if self.rsi > self.thresholds["rsi_overbought"]:
            status = "Sell"

            self.rsi_flag = 0
        elif self.rsi < self.thresholds["rsi_oversold"]:
            status = "Buy"
            self.rsi_flag = 1
        else:
            print("not enough rsi")
            self.rsi_flag = 0

        return
    
    def calculate_historical_rsi(self, period=14):

        """Calculate RSI based on closing prices."""
        period = 14
        BinanceAPI.get_prices(self, 100)
        gains = []
        losses = []

        for i in range(1, len(self.prices)):
            change = self.prices[i] - self.prices[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                losses.append(abs(change))
                gains.append(0)

        # Compute initial average gains and losses
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        rsi_values = []

        for i in range(period, len(self.prices)):
            # Smoothed moving average method
            gain = gains[i - 1]
            loss = losses[i - 1]

            avg_gain = ((avg_gain * (period - 1)) + gain) / period
            avg_loss = ((avg_loss * (period - 1)) + loss) / period

            if avg_loss == 0:
                rs = float("inf")  # Avoid division by zero
            else:
                rs = avg_gain / avg_loss

            rsi = 100 - (100 / (1 + rs))
            rsi_values.append((rsi))
        self.rsi_values = rsi_values
    
        # plt.figure(figsize=(10, 5))
        # plt.plot(rsi_values, label="RSI", color="purple")
        # plt.axhline(self.thresholds["rsi_overbought"], linestyle="--", color="red", label="Overbought (70)")
        # plt.axhline(self.thresholds["rsi_oversold"], linestyle="--", color="green", label="Oversold (30)")
        # plt.title("Relative Strength Index (RSI)")
        # plt.xlabel("Days")
        # plt.ylabel("RSI Value")
        # plt.legend()
        # plt.grid()
        # plt.show()
    
    def calculate_macd(self):
        
        fast_period = self.thresholds["macd_fast_ema"]
        slow_period = self.thresholds["macd_slow_ema"]
        signal_period = self.thresholds["macd_signal_ema"]

        required_period = 100#slow_period + signal_period  # Ensure enough data is fetched
        
        BinanceAPI.get_prices(self, required_period)

        if len(self.prices) < required_period:
            print("Not enough data for MACD")

        # Calculate EMA multipliers
        multiplier_fast = 2 / (fast_period + 1)
        multiplier_slow = 2 / (slow_period + 1)
        multiplier_signal = 2 / (signal_period + 1)

        # Initialize EMA lists with None values
        ema_fast_list = [None] * len(self.prices)
        ema_slow_list = [None] * len(self.prices)

        # Compute first EMA as a simple moving average (SMA)
        ema_fast = sum(self.prices[:fast_period]) / fast_period
        ema_slow = sum(self.prices[:slow_period]) / slow_period

        # Place first EMA values in correct index
        ema_fast_list[fast_period - 1] = ema_fast
        ema_slow_list[slow_period - 1] = ema_slow

        # Compute EMAs iteratively
        for i in range(slow_period, len(self.prices)):
            ema_fast = (self.prices[i] - ema_fast) * multiplier_fast + ema_fast
            ema_slow = (self.prices[i] - ema_slow) * multiplier_slow + ema_slow
            ema_fast_list[i] = ema_fast
            ema_slow_list[i] = ema_slow
        #print("ema fast and slow ", ema_fast_list, ema_slow_list)
        macd_line = [None] * len(self.prices)
        for i in range(len(self.prices)):
            if ema_fast_list[i] is not None and ema_slow_list[i] is not None:
                macd_line[i]=(ema_fast_list[i] - ema_slow_list[i])
            

        # Filter out None values for signal line calculation
        valid_macd = [m for m in macd_line if m is not None]
        #print("valid macd ", valid_macd)
        if len(valid_macd) < signal_period:
            print("valid less than signal")

        # Compute first Signal EMA
        signal_ema = sum(valid_macd[:signal_period]) / signal_period
        signal_line = [None] * (slow_period + signal_period - 2) + [signal_ema]

        for i in range(0, len(valid_macd)):
            signal_ema = (valid_macd[i] - signal_ema) * multiplier_signal + signal_ema
            signal_line.append(signal_ema)
        #print("signal ema ", signal_ema)
        # Ensure valid MACD and Signal Line before generating signals
        if len(macd_line) < 2 or len(signal_line) < 2 or macd_line[-1] is None or macd_line[-2] is None:
            print("wrong macd and singal")
        #print("macd line ", macd_line)
        #print("signal line ", signal_line)
        # Generate Buy/Sell/Hold signals
        if (
        macd_line[-1] is not None and macd_line[-2] is not None and 
        signal_line[-1] is not None and signal_line[-2] is not None
        ):
            if macd_line[-1] > signal_line[-1] and macd_line[-2] <= signal_line[-2]:
                self.macd_flag = 1
                status = "Buy"
            elif macd_line[-1] < signal_line[-1] and macd_line[-2] >= signal_line[-2]:
                self.macd_flag = 0
                status =  "Sell"
            else:
                self.macd_flag = 0

                status = "Hold"
        else:
            self.macd_flag = 0
            print("Not enough data for MACD signals")

        # Example usage (assuming macd_line and signal_line are already computed)
        # Remove None values for proper plotting
        self.macd_line_filtered = [m for m in macd_line  ]
        self.signal_line_filtered = [s for s in signal_line]

        #plot_macd(macd_line_filtered, "macd line", signal_line_filtered, "signal line")
        self.macd = 0

    def calculate_supertrend(self):
        """Calculates Supertrend using risk-based parameters."""
        atr_period = self.thresholds["supertrend_atr_period"]
        multiplier = self.thresholds["supertrend_multiplier"]
        #period = atr_period * 3
        period = 100
        BinanceAPI.get_prices(self, period)
        
        tr_list  = []
        atr = [None] * len(self.prices)
        supertrend = [None] * len(self.prices)
        for i in range(len(self.prices)):
            tr = max(self.highs[i] - self.lows[i],
                     abs(self.highs[i] - self.prices[i - 1]) if i > 0 else 0,
                     abs(self.lows[i] - self.prices[i - 1]) if i > 0 else 0)
            tr_list.append(tr)
             # Compute First ATR value using SMA
        atr[atr_period - 1] = sum(tr_list[:atr_period]) / atr_period  # First ATR is SMA

            # Compute Remaining ATR values using EMA formula
        for i in range(atr_period, len(self.prices)):
            atr[i] = ((atr[i - 1] * (atr_period - 1)) + tr_list[i]) / atr_period  # EMA ATR formula
        upper = [None]* len(self.prices)
        lower = [None]* len(self.prices)

        multiplier = 1
        for i in range(atr_period, len(self.prices)):   
            mid = (self.highs[i] + self.lows[i]) / 2
            upper[i] = mid + (multiplier * atr[i])
            lower[i] = mid - (multiplier * atr[i])
            if i == atr_period:
                supertrend[i] = (lower[i])
            else:

                if self.prices[i] > supertrend[i-1]:
                    supertrend[i] = lower[i]
                else:
                    supertrend[i] = upper[i]
            #print("price  -", self.prices[i], atr[i],upper[i], lower[i])  
        """Generates Buy or Sell signals based on Supertrend."""
    
        green_line = [None] * len(self.prices)
        red_line = [None] * len(self.prices)
        for i in range(atr_period, len(self.prices)):
            if supertrend[i] < self.prices[i]:
                green_line[i] = supertrend[i]
            else:
                red_line[i] = supertrend[i]
        self.supertrend_green = [m for m in green_line ]
        self.supertrend_prices = [s for s in self.prices ]
        self.supertrend_red = [p for p in red_line]

        min_supertrend = min(s for s in supertrend if s != None)
        max_supertrend = max(s for s in supertrend if s != None)
        #plot_macd(min_supertrend-5000, max_supertrend+5000, macd_line_filtered, "buy", signal_line_filtered, "prices", price_line, "sell")

        signals = [None] * len(self.prices)
        for i in range(atr_period+1, len(self.prices)):
            # if supertrend[i] is None or supertrend[i-1] is None:
            #     continue
            if i > 0 and self.prices[i] > supertrend[i] and self.prices[i - 1] < supertrend[i - 1]:
                signals[i] = "BUY"
            elif i > 0 and self.prices[i] < supertrend[i] and self.prices[i - 1] > supertrend[i - 1]:
                signals[i]="SELL"
            else:
                signals[i]="HOLD"
            #print(self.prices[i], supertrend[i], signals[i])
        self.supertrend = supertrend[-1]
        if signals[-1]=="BUY":
            self.st_flag = 1
        elif signals[-1]=="SELL":
            self.st_flag=0
        else:
            print("not enough st")
            self.st_flag=0

        
import matplotlib.pyplot as plt

def plot_macd(min, max, macd_line, label_1, signal_line, label_2, prices, label_3):

    plt.figure(figsize=(10, 5))
    plt.ylim(min, max)
    if label_1 != "none":
        plt.plot(macd_line, label=label_1, color='green')
    if label_2 != "none": 
          plt.plot(signal_line, label=label_2, color='blue')
    if label_3 != "none":
        plt.plot(prices, label = label_3, color = 'red')
    plt.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.title('MACD and Signal Line')
    plt.legend()
    plt.show()


