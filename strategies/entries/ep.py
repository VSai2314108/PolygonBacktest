from datetime import datetime, timedelta

from dataloader.dataloader import DataLoader
from objs.trades import Trade
class EP():
    class EPDataloader(DataLoader):
        def __init__(self, symbol, start_date: datetime, end_date: datetime, tf: tuple, backfill: timedelta) -> None:
            super().__init__(symbol, start_date, end_date, tf, backfill)
            # average volume over 20 days
            self.df['avg_volume'] = self.df['volume'].rolling(20).mean().shift(1)
            self.df['gap'] = self.df['open']/self.df['close'].shift(1) - 1 > 0.03
            self.df['breaks_high'] = self.df['high'] > self.df['high'].shift(1)
            
            self.df['atr'] = self.df['high'] - self.df['low']
            self.df['atr_range'] = self.df['atr'].rolling(20).mean().shift(1)
            
    
    def __init__(self, symbol, start_date: datetime, end_date: datetime):
        self.dataloader = EP.EPDataloader(symbol, start_date, end_date, (1, "day"), timedelta(days=20))
        self.stop, self.entry, self.targets, self.gap_date, self.gap_loc = None, None, None, None, None
        self.symbol = symbol
        
    def algorithim(self, bar):
        if self.entry == None:
            if bar['volume'] > bar['avg_volume']*2 and bar['volume'] > 1000000 and bar['gap'] and bar['breaks_high']:
                self.gap_date = bar['time']
                self.stop = bar['low']
                self.entry = bar['high']
                self.targets = [self.entry+(self.entry-self.stop), self.entry+(self.entry-self.stop)*2, self.entry+(self.entry-self.stop)*3]
        else: # we have an entry
            if bar['high'] > self.entry:
                if bar['open'] < self.entry: # ensure we dont cross entry price via second gap
                    trade = Trade(self.symbol, bar['time'], [(bar['time'], self.entry, 1)], self.stop, self.targets)
                    self.entry, self.stop, self.targets = None, None, None
                    return trade
            # five days have passed
            elif bar['time'] - self.gap_date > timedelta(days=5):
                self.entry, self.stop, self.targets = None, None, None
            else:
                self.stop = min(self.stop, bar['low'])
                self.entry = bar['high']
                
            
        
    def run(self):
        trades = []
        bar = self.dataloader.get_bar()
        while type(bar) != type(None):
            trade = self.algorithim(bar)
            if trade:
                trades = [trade] + trades
            bar = self.dataloader.get_bar()
        return trades
    
        
        
        