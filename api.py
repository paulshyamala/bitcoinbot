import requests
from datetime import datetime, timedelta
import matplotlib.dates as mdates


class BinanceAPI:
    API_BASE_URL= "https://api.binance.com/api/v3"
    @staticmethod
    def get_ticker_price( symbol="BTCUSDT"):
            """Fetch the latest price for a given symbol from Binance Testnet."""
            endpoint = f"{BinanceAPI.API_BASE_URL}/ticker/price"
            params = {"symbol": symbol}
            try:
                response = requests.get(endpoint, params=params, timeout=10)
                response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
                data = response.json()
                return float(data["price"])
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")
                return(f"API Request error")
            except ValueError:
                print( f"Error: Could not parse response. {response.status_code}, {response.text}")
                return(-f"Error: Could not parse API response.")
            except KeyError:
                print( f"Error: Unexpected response format.{response.status_code}, {response.text}")
                return(f"Error: Unexpected response API format.")
            
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
        endpoint = f"{BinanceAPI.API_BASE_URL}/klines"

        from_ts = given_date - timedelta(days=1)
        from_ts = int(from_ts.timestamp() * 1000) 
        to_ts = int(given_date.timestamp() * 1000) 

        params = {
            "symbol": "BTCUSDT",
            "interval": "1d",
            "startTime": from_ts,
            "endTime": to_ts
        }

        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data:
                closing_price = float(data[0][4])  # The 5th element is the "Close" price
                return closing_price
            else:
                print( "No data found for that day.")
                return("No data found for that day.")
        
        except requests.exceptions.RequestException as e:
            print( f"Request error: {e}")
            return(f"Request error: {e}")
        except (ValueError, KeyError, IndexError) as e:
            print( f"Data processing error: {e}")
            return(f"Data processing error: {e}")
        
    @staticmethod  
    def get_prices_day_range(data, from_date, to_date):
        """
        Fetches closing, high, and low prices from Binance API for a date range.

        Parameters:
            from_date (str): Start date in 'YYYY-MM-DD' format.
            to_date (str): End date in 'YYYY-MM-DD' format.
        """
        endpoint = f"{BinanceAPI.API_BASE_URL}/klines"
        from_ts = int(from_date.timestamp() * 1000)
        to_ts = int(to_date.timestamp() * 1000)

        params = {
            "symbol": "BTCUSDT",
            "interval": "1d",
            "startTime": from_ts,
            "endTime": to_ts
        }

        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            response_data = response.json()

            data.prices = [float(candle[4]) for candle in response_data]  # Closing prices
            data.highs = [float(candle[2]) for candle in response_data]   # High prices
            data.lows = [float(candle[3]) for candle in response_data]    # Low prices
            return(len(data.prices))

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return(0)
        except (ValueError, KeyError, IndexError) as e:
            print(f"Data processing error: {e}")
            return(0)
    
    @staticmethod 
    def get_ohlc_day_range(from_date, to_date):
        """
        Fetches closing, high, and low prices from Binance API for a date range.

        Parameters:
            from_date (str): Start date in 'YYYY-MM-DD' format.
            to_date (str): End date in 'YYYY-MM-DD' format.
        """
        endpoint = f"{BinanceAPI.API_BASE_URL}/klines"
        from_ts = int(from_date.timestamp() * 1000)
        to_ts = int(to_date.timestamp() * 1000)

        params = {
            "symbol": "BTCUSDT",
            "interval": "1d",
            "startTime": from_ts,
            "endTime": to_ts
        }

        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            response_data = response.json()

            ohlc_data = []
            for candle in response_data:
                timestamp = datetime.fromtimestamp(candle[0] / 1000)
                ohlc_data.append([
                    mdates.date2num(timestamp),
                    float(candle[1]),  # Open
                    float(candle[2]),  # High
                    float(candle[3]),  # Low
                    float(candle[4])   # Close
                ])
            return ohlc_data

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except (ValueError, KeyError, IndexError) as e:
            print(f"Data processing error: {e}")
            return None
