from objs.trades import Trade
from dataloader.dataloader import DataLoader

from datetime import datetime, timedelta

class Targets():
    class TargetsDataloader(DataLoader):
        def __init__(self, symbol, start_date: datetime, end_date: datetime, tf: tuple, backfill: timedelta) -> None:
            super().__init__(symbol, start_date, end_date, tf, backfill)
    
    def __init__(self, trade: Trade):
        self.target = 0
        self.trade = trade
        self.dataloader = Targets.TargetsDataloader(trade.symbol, trade.date, trade.date + timedelta(days=50), (1, 'day'), timedelta(days=0))
    
    def algorithim(self, bar):
        q =  self.trade.remaining if self.target == len(self.trade.targets) - 1 else self.trade.remaining/2.0
        if bar['high'] > self.trade.targets[self.target]:
            self.trade.add_trade((bar['time'], self.trade.targets[self.target], -q))
            self.target+=1
        elif bar['low'] < self.trade.stop:
            self.trade.add_trade((bar['time'], self.trade.stop, -self.trade.remaining))

    
    def run(self):
        bar = self.dataloader.get_bar()
        while type(bar) != type(None):
            self.algorithim(bar)
            bar = self.dataloader.get_bar()
            
            if self.trade.remaining == 0:
                return 
            # elif bar == None:
            #     self.dataloader.extend(timedelta(days=50))
        if self.trade.remaining != 0:
            self.trade.add_trade((self.dataloader.visible_df.iloc[-1]['time'],
                                  self.dataloader.visible_df.iloc[-1]['close'], 
                                  -self.trade.remaining)
                                 )
    