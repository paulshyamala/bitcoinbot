import requests
import datetime
import matplotlib.dates as mdates
import time

class BinanceAPI:
    @staticmethod
    def get_ticker_price( symbol="BTCUSDT"):

            BASE_URL = "https://testnet.binance.vision/api"
            """Fetch the latest price for a given symbol from Binance Testnet."""
            endpoint = f"{BASE_URL}/v3/ticker/price"
            params = {"symbol": symbol}
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                data = response.json()
                return float(data["price"])
            else:
                return f"Error: {response.status_code}, {response.text}"
            
    @staticmethod
    def get_btc_ohlc():
            """Fetches the last 30 days of BTC/USDT OHLC data from Binance API."""
            url = "https://api.binance.com/api/v3/klines"
            params = {"symbol": "BTCUSDT", "interval": "1d", "limit": 30}
            response = requests.get(url, params=params).json()

            ohlc_data = []
            for candle in response:
                timestamp = datetime.datetime.fromtimestamp(candle[0] / 1000)
                ohlc_data.append([
                    mdates.date2num(timestamp),
                    float(candle[1]),  # Open
                    float(candle[2]),  # High
                    float(candle[3]),  # Low
                    float(candle[4])   # Close
                ])
            return ohlc_data
    
    @staticmethod
    def get_prices(data, period):
            """Fetches closing prices from Binance API based on the given period."""
            url = "https://api.binance.com/api/v3/klines"
            params = {"symbol": "BTCUSDT", "interval": "1d", "limit": period}
            response = requests.get(url, params=params).json()

            data.prices = [float(candle[4]) for candle in response]  # Store closing prices
            data.highs = [float(candle[2]) for candle in response]  # Extract High prices
            data.lows = [float(candle[3]) for candle in response]  # Extract Low prices
            
    

    @staticmethod
    def get_price_on_day(given_date):
        """
        Fetch the closing price for a given symbol on a specific day from Binance Testnet.

        Parameters:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT")
            date_str (str): Date in "YYYY-MM-DD" format

        Returns:
            float: Closing price for that day, or error message if not found.
        """
        BASE_URL = "https://testnet.binance.vision/api"
        endpoint = f"{BASE_URL}/v3/klines"

        start_time = int(given_date.timestamp() * 1000)
        end_time = given_date + datetime.timedelta(days=1)
        end_time = int(end_time.timestamp() * 1000)

        params = {
            "symbol": "BTCUSDT",
            "interval": "1d",
            "startTime": start_time,
            "endTime": end_time,
            "limit": 1
        }

        response = requests.get(endpoint, params=params)

        if response.status_code == 200:
            data = response.json()
            if data:
                closing_price = float(data[0][4])  # The 5th element is the "Close" price
                return closing_price
            else:
                return "No data found for that day."
        else:
            return f"Error: {response.status_code}, {response.text}"
        
    @staticmethod  
    def get_prices_day_range(data, from_date, to_date):
        """
        Fetches closing, high, and low prices from Binance API for a date range.

        Parameters:
            from_date (str): Start date in 'YYYY-MM-DD' format.
            to_date (str): End date in 'YYYY-MM-DD' format.
        """
        url = "https://api.binance.com/api/v3/klines"
        from_ts = int(from_date.timestamp() * 1000)
        to_ts = int(to_date.timestamp() * 1000)

        params = {
            "symbol": "BTCUSDT",
            "interval": "1d",
            "startTime": from_ts,
            "endTime": to_ts
        }

        response = requests.get(url, params=params).json()

        data.prices = [float(candle[4]) for candle in response]  # Closing prices
        data.highs = [float(candle[2]) for candle in response]   # High prices
        data.lows = [float(candle[3]) for candle in response]    # Low prices
    
    @staticmethod 
    def get_ohlc_day_range(from_date, to_date):
        """
        Fetches closing, high, and low prices from Binance API for a date range.

        Parameters:
            from_date (str): Start date in 'YYYY-MM-DD' format.
            to_date (str): End date in 'YYYY-MM-DD' format.
        """
        url = "https://api.binance.com/api/v3/klines"
        from_ts = int(from_date.timestamp() * 1000)
        to_ts = int(to_date.timestamp() * 1000)

        params = {
            "symbol": "BTCUSDT",
            "interval": "1d",
            "startTime": from_ts,
            "endTime": to_ts
        }

        response = requests.get(url, params=params).json()
        ohlc_data = []
        for candle in response:
            timestamp = datetime.datetime.fromtimestamp(candle[0] / 1000)
            ohlc_data.append([
                mdates.date2num(timestamp),
                float(candle[1]),  # Open
                float(candle[2]),  # High
                float(candle[3]),  # Low
                float(candle[4])   # Close
            ])
        return ohlc_data
       