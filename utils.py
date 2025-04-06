from datetime import datetime
import pytz

class Utils:
    @staticmethod
    def get_localtime():
        # Define the Dubai timezone using the pytz library
        dubai_tz = pytz.timezone("Asia/Dubai")

        # Get the current local time in Dubai, adjusting for the timezone
        dubai_time = datetime.now(dubai_tz)

        # Return the current date and time as a datetime object
        return dubai_time  # The full datetime object, not formatted yet
    
    @staticmethod
    def get_localdate():
        # Define the Dubai timezone using the pytz library
        dubai_tz = pytz.timezone("Asia/Dubai")

        # Get the current local time in Dubai, adjusting for the timezone
        dubai_time = datetime.now(dubai_tz)

        # Return only the date part of the current time, formatted as 'YYYY-MM-DD'
        return dubai_time.strftime("%Y-%m-%d")  # Returns a string formatted as 'YYYY-MM-DD'
    
    @staticmethod
    def get_date():
        # Define the Dubai timezone using the pytz library
        dubai_tz = pytz.timezone("Asia/Dubai")

        # Get the current local time in Dubai, adjusting for the timezone
        dubai_time = datetime.now(dubai_tz)

        # Return the current date and time as a datetime object
        return dubai_time  # The full datetime object, like 'get_localtime', but no formatting
