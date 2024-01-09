from datetime import datetime, timedelta
from polygon.rest import RESTClient
from polygon.rest.models import Agg
from typing import List

class PolygonClient:
    
    def __init__(self, api_key):
        self.client: RESTClient = RESTClient(api_key)
        
    def get_fundamentals(self, symbol):
        return self.client.get_ticker_details(symbol)
        
    def get_minute_data(self, symbol, date):
        """
        Minute bars for chart
        """
        initial_timestamp = datetime.strptime(date, '%Y-%m-%d')
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
    
    