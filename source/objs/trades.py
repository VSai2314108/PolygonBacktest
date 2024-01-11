from datetime import datetime
from typing import List

class Trade:
    def __init__(self, symbol, date, trades = None, stop = None, targets = None):
        self.symbol = symbol
        self.date: datetime = date
        self.stop = stop
        self.targets = targets
        self.trades: List[tuple] = trades # (timestamp, price, quantity as a factor of 1)
        self.remaining = sum([trade[2] for trade in trades])
    
    def add_trade(self, trade):
        self.trades.append(trade)
        self.remaining += trade[2]
    
    def compute_r(self):
        """
        R: The distance between the first trade and stop
        """
        r = self.trades[0][1] - self.stop
        
        total = 0
        # compute the r frm the rest of the trades
        for trade in self.trades[1:]:
            total += (trade[1] - self.stop)*(-trade[2])
        
        return total/r
    
    def __str__(self):
        return f"{self.symbol} {self.date} {self.trades} {self.stop} {self.targets}"