from datetime import date, datetime, timedelta
from typing import List
import pandas as pd
import os

from scanners.scanner import Scanners
from clients.polygon import PolygonClient
from universe.universe import Universe
from objs.trades import Trade

from .entries.washout import WashoutLong
from .entries.gapswings import GapAndGo
from .exits.target import Target
from .exits.Sma9 import Sma9

class algorithim():
    polygon = PolygonClient()
    
    entry = {
        "washout": (WashoutLong(), (1, "min")),
        "gapandgo": (GapAndGo(), (1, "day"))
    }
    
    exit = {
        "target": Target(),
        "sma9": Sma9()
    }
    
    
    def __init__(self, entrystrat, exitstrat, scanner, universe, start_date: datetime, end_date: datetime):
        self.entrystrat = entrystrat
        self.exitstrat = exitstrat
        self.start_date = start_date
        self.end_date = end_date
        self.universe: Universe = Universe(universe)
        self.scanner: Scanners = Scanners(self.polygon, self.universe, scanner)
        self.trades: List[Trade] = []

        
    def run(self):
        """
        The process is as follows
        1. Get all tickers and possible days trades could be initiated
        2. Run the entry algorithim on each day and return None or a trade with entry and targets
        3. Specify the valid exit algorithms for each entry algorithm this should include a time frame
        """
        days: List[tuple] = self.scanner.run_scanner(self.start_date, self.end_date)
        out = []
        for symbol, date in days: 
            trade: Trade = self.entry[self.entrystrat][0].algorithim(symbol, date)
            if trade:
                self.exit[self.exitstrat].evaluate(trade, self.entry[self.entrystrat][1])
                print(trade)
                out.append(trade)
        self.trades = out
        return out

    def to_csv(self):
        # add the trades to a dataframe
        df: pd.DataFrame = pd.DataFrame(columns=["symbol", "date", "stop", "targets", "trades"])
        for trade in self.trades:
            df.loc[len(df)] = [trade.symbol, trade.date, trade.stop, trade.targets, trade.trades]
        # check if the directory exists
        if not os.path.exists(f"results/{self.entrystrat}"):
            os.makedirs(f"results/{self.entrystrat}")
        df.to_csv(f"results/{self.entrystrat}/{self.exitstrat}_{self.start_date.strftime('%Y-%m-%d')}_{self.end_date.strftime('%Y-%m-%d')}.csv")
                
            
                
        
        
        