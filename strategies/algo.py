from datetime import datetime
from typing import List
import pandas as pd
import os

from scanners.scanner import Scanners
from clients.polygon import PolygonClient
from universe.universe import Universe
from objs.trades import Trade

from .entries.ep import EP
from .exits.targets import Targets



class algo():
    strategy_scanners = {
        "ep": "fundamentals"
    }
    
    exits = {
        "targets": Targets
    }
    
    entries = {
        "ep": EP
    }
    
    def __init__(self, strategy, exits, start_date: datetime = datetime(2023, 1, 1), end_date: datetime = datetime(2024, 1, 1)) -> None:
        trading_days = Scanners(Universe("/Users/vsai23/Workspace/PolygonBacktest/tv.csv"), self.strategy_scanners[strategy]).run_scanner(start_date, end_date)
        self.trades: List[Trade] = [] 
        self.entrystrat = strategy
        self.exitstrat = exits
        self.start_date = start_date
        self.end_date = end_date
        
        for symbol, date in trading_days:
            ep = self.entries[strategy](symbol, date, end_date)
            
            trades = ep.run()
            for trade in trades:
                self.exits[exits](trade).run()
                self.trades.append(trade)
                print(trade)

    
    def to_csv(self):
        # add the trades to a dataframe
        df: pd.DataFrame = pd.DataFrame(columns=["symbol", "date", "stop", "targets", "trades"])
        for trade in self.trades:
            df.loc[len(df)] = [trade.symbol, trade.date, trade.stop, trade.targets, trade.trades]
        # check if the directory exists
        if not os.path.exists(f"results/{self.entrystrat}"):
            os.makedirs(f"results/{self.entrystrat}")
        df.to_csv(f"results/{self.entrystrat}/{self.exitstrat}_{self.start_date.strftime('%Y-%m-%d')}_{self.end_date.strftime('%Y-%m-%d')}.csv")


    
    
            
        
        

