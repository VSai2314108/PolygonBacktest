from datetime import datetime, timedelta
from .dataloader import DataLoader

class DataLoaderSmas(DataLoader):
    def __init__(self, symbol, start_date: datetime, end_date: datetime, tf: tuple, backfill: timedelta) -> None:
        super().__init__(symbol, start_date, end_date, tf, backfill)
        self.df['sma_10'] = self.df['close'].rolling(10).mean()
        self.df['sma_20'] = self.df['close'].rolling(20).mean()
        self.df['sma_50'] = self.df['close'].rolling(50).mean()