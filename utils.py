from datetime import datetime
import pytz

class Utils:
    @staticmethod
    def get_localtime():
        # Define the Dubai timezone
        dubai_tz = pytz.timezone("Asia/Dubai")

        # Get the current time in Dubai
        dubai_time = datetime.now(dubai_tz)

        return dubai_time#.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def get_localdate():
        # Define the Dubai timezone
        dubai_tz = pytz.timezone("Asia/Dubai")

        # Get the current time in Dubai
        dubai_time = datetime.now(dubai_tz)

        return dubai_time.strftime("%Y-%m-%d")
    
    @staticmethod
    def get_date():
        # Define the Dubai timezone
        dubai_tz = pytz.timezone("Asia/Dubai")

        # Get the current time in Dubai
        dubai_time = datetime.now(dubai_tz)

        return dubai_time

