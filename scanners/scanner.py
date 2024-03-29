from datetime import datetime, timedelta
from polygon.rest import RESTClient
from polygon.rest.models import Agg
from typing import List

from clients.polygon import PolygonClient
from universe.universe import Universe

class Scanners:
    """
    These classes are written as a way to scan stocks to be used in backtesting \n
    They do not have a live trading equivalent \n
    Instead they must be converted for live trading via a class call LiveScanners \n
    In certain cases they have slight look forward bias, but this is mostly for ease of use \n
    """
    client = PolygonClient()
    def __init__(self, universe: Universe, scanner: str):
        # define a map with scanner names as keys and scanner functions as values
        scanners = {
            "gap_trading": (self.gap_trading_scanner, (1, "day")),
            "swing_trading": (self.swing_trading_scanner, (1, "day")),
            "fundamentals": (self.basic_scanner, (1, "day")),
        }
        self.scanner, self.tf = scanners[scanner]
        self.tickers = universe.get_tickers()
        
    def basic_scanner(self, symbol, stock_data: List[Agg]) -> List[tuple]:
        # return the first day of the stock
        details = self.client.get_fundamentals(symbol)
        mkt_cap_big = details.market_cap > 1000000000
        if mkt_cap_big:
            return [(symbol, datetime.fromtimestamp(stock_data[0].timestamp / 1000))]
        return []
    
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
                    date = datetime.fromtimestamp(current_day.timestamp / 1000)
                    out = out + [(symbol, date)]
        return out
    
    def swing_trading_scanner(self, symbol, stock_data: List[Agg]) -> List[tuple]:
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
            gap_up = current_day.open > (previous_day.close * 1+(max(0.02, 2*adr_p)))
            outside_range = current_day.open > previous_day.high
            not_small = current_day.open >= 5
            high_dollar_volume = (avg_volume * current_day.close) > 100000000
            adr_p_over = adr_p > 0.03
            
            if gap_up and outside_range and not_small and high_dollar_volume and high_avg_volume and adr_p_over and mkt_cap_big:
                date = datetime.fromtimestamp(current_day.timestamp / 1000)
                out = out + [(symbol, date)]
        return out
    
    def run_scanner(self, start_date, end_date):
        """
        Output format of List[tuple] is [(symbol, date)...]
        """
        out: List = []
        for ticker in self.tickers:
            try:
                data = self.client.get_stock_data(ticker, start_date, end_date, self.tf)
                out = out + self.scanner(ticker, data)
            except Exception as e:
                print("Error with ticker: " + ticker + " " + str(e))
        return out