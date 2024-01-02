from datetime import datetime, timedelta
from numpy import poly
from polygon.rest import RESTClient
from polygon.rest.models import Agg
from typing import List

from .PolygonClient import PolygonClient
from .Universe import Universe

class Scanners:
    def __init__(self, client: PolygonClient, universe: Universe, scanner: str):
        self.client: PolygonClient = client
        # change this to a switch statement to initiate different scanners
        if scanner == "gap_trading":
            self.scanner = self.gap_trading_scanner
        self.tickers = universe.get_tickers()
        
    def gap_trading_scanner(self, symbol, stock_data: List[Agg]) -> List[tuple]:
        out = []
        
        # fundamentals
        details = self.client.get_fundamentals(symbol)
        mkt_cap_big = details.market_cap > 2000000000
        
        for i in range(20, len(stock_data)):
            avg_volume = sum([day.volume for day in stock_data[i-20:i]]) / 20
            adr_p = sum([abs(day.high - day.low) / day.close for day in stock_data[i-20:i]]) / 20
            
            # technicals
            high_avg_volume = avg_volume > 1000000
            previous_day = stock_data[i-1]
            current_day = stock_data[i]
            gap_up = current_day.open > (previous_day.close * 1.02)
            outside_range = current_day.open > previous_day.high
            not_small = current_day.open >= 5
            high_dollar_volume = (avg_volume * current_day.close) > 100000000
            adr_p_over = adr_p > 0.02
            
            # check pre market volume
            if gap_up and outside_range and not_small and high_dollar_volume and high_avg_volume and adr_p_over and mkt_cap_big:
                date = datetime.fromtimestamp(current_day.timestamp / 1000).strftime('%Y-%m-%d')
                pre_market_data = self.client.get_minute_data(symbol, datetime.fromtimestamp(current_day.timestamp / 1000).strftime('%Y-%m-%d'))
                pre_market_end_time = datetime.fromtimestamp(current_day.timestamp / 1000) + timedelta(hours=9, minutes=30)
                pre_market_volume = sum(minute.volume for minute in pre_market_data if minute.timestamp / 1000 < pre_market_end_time.timestamp())
                pre_market_liquid = pre_market_volume > 10000
            

                if pre_market_liquid:
                    date = datetime.fromtimestamp(current_day.timestamp / 1000).strftime('%Y-%m-%d')
                    out = out + [(symbol, date)]
        return out
    
    def run_scanner(self, start_date, end_date):
        # format of out is alwyas [(symbol, date)...]
        out: List[tuple] = []
        for ticker in self.tickers:
            try:
                data = self.client.get_stock_data(ticker, start_date, end_date)
                out = out + self.scanner(ticker, data)
            except:
                print("Error with ticker: " + ticker)
        return out