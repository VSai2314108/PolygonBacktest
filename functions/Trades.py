from datetime import datetime
class Trade:
    def __init__(self, symbol, timestamp, entry, stop, targets, success):
        self.symbol = symbol
        self.date: datetime = timestamp
        self.entry = entry
        self.stop = stop
        self.targets = targets
        self.success = success
        self.r = None
    
    def __str__(self) -> str:
        return f"Trade: Ticker - {self.symbol}, Date - {self.date.isoformat()}, Entry - {self.entry}, Stop - {self.stop}, Targets - {self.targets}, Success - {self.success}"    