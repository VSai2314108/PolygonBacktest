from datetime import datetime, timedelta
from polygon.rest import RESTClient
from polygon.rest.models import Agg

from typing import List
import pandas as pd
from datetime import datetime, timedelta

class PolygonClient:
    
    def __init__(self, api_key):
        self.client: RESTClient = RESTClient(api_key)
        
    def __init__(self):
        self.client: RESTClient = RESTClient()
        
    def get_fundamentals(self, symbol):
        return self.client.get_ticker_details(symbol)
        
    def get_minute_data(self, symbol, date):
        """
        Minute bars for chart
        """
        initial_timestamp = None
        if type(date) == str:
            initial_timestamp = datetime.strptime(date, '%Y-%m-%d')
        else:
            initial_timestamp = date
        # set timestamp time to 00:00
        initial_timestamp = initial_timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        timestamp_930_am = initial_timestamp + timedelta(hours=4, minutes=30)
        timestamp_2_hours_later = timestamp_930_am + timedelta(hours=8)
        return self.client.get_aggs(symbol, 1, "minute", timestamp_930_am, timestamp_2_hours_later)

    def get_day_data(self, symbol, date):
        """
        Daily bars for chart
        """
        initial_timestamp = datetime.strptime(date, '%Y-%m-%d')
        timestamp_history = initial_timestamp - timedelta(days=250)
        timestamp_day = initial_timestamp
        return self.client.get_aggs(symbol, 1, "day", timestamp_history, timestamp_day)
    
    def get_stock_data(self, symbol, start_date, end_date, tf = (1,"day")):
        """
        Daily bars for analysis
        tf = (1, "day")
        """
        return self.client.get_aggs(symbol, tf[0], tf[1], start_date, end_date)
    
    def convert_aggs(self, data: List[Agg]):
        """
        Converts a list of Agg objects to a dataframe
        """
        
        # Columns: time | open | high | low | close | volume 
        df: pd.DataFrame = pd.DataFrame({}, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        for agg in data:
            row = {'time': datetime.fromtimestamp(agg.timestamp/1000), 
                'open': agg.open, 
                'high': agg.high, 
                'low': agg.low, 
                'close': agg.close, 
                'volume': agg.volume}
            df.loc[len(df)] = row
        return df
    
    