from datetime import datetime, timedelta
from clients.polygon import PolygonClient
class DataLoader:
    """
    Base class for all data loaders \n
    Provides a common interface for all data loaders \n
    Data loaders should extend this class to add indicators to the core df \n
    """
    polygon = PolygonClient()
    
    def __init__(self, symbol, start_date: datetime, end_date: datetime, tf: tuple, backfill: timedelta) -> None:
        start_date = start_date - backfill
        self.symbol = symbol
        self.df = self.polygon.convert_aggs(self.polygon.get_stock_data(symbol, start_date, end_date, tf))
        
        # find index of row with start_date
        self.cur = 0
        for i in range(len(self.df)):
            if self.df.iloc[i]['time'] >= start_date:
                self.cur = i
                break
        
        self.visible_df = self.df.iloc[:self.cur]

    
    def get_bar(self):
        # check if we are at the end of the df
        if self.cur >= len(self.df):
            return None
        
        out = self.df.iloc[self.cur]
        self.cur += 1
        self.visible_df = self.df.iloc[:self.cur] # inclusive of current bar
        return out
    
    def extend(self, time: timedelta):
        self.add_df = self.polygon.convert_aggs(self.polygon.get_stock_data(self.symbol, self.df.iloc[-1]['time'], self.df.iloc[-1]['time']+time, self.tf))
        self.df = self.df.append(self.add_df)
    
    
    