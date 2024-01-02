from typing import List
from polygon.rest.models import Agg
from datetime import date, datetime, time
import pandas as pd

from .Strategy import Strategy
from .Trades import Trade
from .Scanners import Scanners
from .PolygonClient import PolygonClient

class WashoutLong(Strategy):
    def __init__(self, scanner: Scanners, client: PolygonClient):
        self.client: PolygonClient = client
        self.tickers: List[tuple] = scanner.run_scanner(date(2023, 1, 1), date(2023, 12, 31))
        self.trades: List[Trade] = []
    
    def algorithim(self, symbol, data: List[Agg]):
        # find the index of the first candle with a timestamp >= 9:30
        ninethirty = None
        stop = None
        entry = None
        for i in range(len(data)):
            if datetime.fromtimestamp(data[i].timestamp / 1000).time() >= time(9, 30):
                ninethirty = i
                break
        
        i = i+1 # increment i to the next candle
        
        # check we at least have one lower low

        # the washout can happen at any point in the first 5 minutes
        for j in range(5):
            counter = 0
            while (data[i+j].low < data[i+j-1].low):
                # can't have a huge drop
                if data[i+j].high > data[i+j-1].high:
                    i = i+j
                    break
                if counter > 5:
                    return
                i = i + 1
                counter +=1
            if i != ninethirty + 1:
                i = i + j
                break
                
        # verify that there is a washout 
        if i == ninethirty + 1:
            return 
        
        # set the stop as low of day
        stop = data[i-1].low
        entry = data[i-1].high
        
        if data[ninethirty].low < stop:
            return
        
        # find the first new high
        while (data[i].high < data[i-1].high):
            # we want the low of day as the stop
            stop = min(data[i].low, stop)
            i = i + 1
        
        # entry and target
        stop = min(data[i-1].low, stop)
        entry = min(entry, data[i-1].high)
        target = entry + (entry - stop)
        target2 = entry + (entry - stop) * 2 # for later use if we want to proceed to two r
        
        """
        Variations
        1: target is 1r all is sold here
        2r entry stop: half sold at 1r half sold till 2r or entry priced is reached 
        2r same stop: half sold at 1r half sold till 2r or stop is reached
        ema stop: half sold at 1r half sold till 2r or ema is reached 
        
        Variations of code are simple so they are not saved here
    
        """
        # check whether target or stop is hit
        for j in range(i+1, len(data)):
            if data[j].low <= stop:
                return Trade(symbol, datetime.fromtimestamp(data[ninethirty].timestamp/ 1000), entry, stop, [target], -1)
            elif data[j].high >= target:
                # modify this to check if target 2 is hit before the entry price is touched again
                # target2 = entry + (entry - stop) * 2 # for later use if we want to proceed to two r
                # if current price is less than 9 sma sell the whole position
                sma9 = sum([data[l].close for l in range(j-8, j+1)]) / 9
                if data[j].close <= sma9:
                    return Trade(symbol, datetime.fromtimestamp(data[ninethirty].timestamp/ 1000), entry, stop, [target], 1)
                for k in range(j, len(data)):
                    # calculate the 9 period ema
                    sma9 = sum([data[l].close for l in range(k-8, k+1)]) / 9
                    if data[k].close <= sma9:
                        r = max(0.01, entry-stop)
                        return Trade(symbol, datetime.fromtimestamp(data[ninethirty].timestamp/ 1000), entry, stop, [target, data[k].close], 0.5+0.5*((data[k].close - entry)/r))

    
    def evaluate(self):
        for symbol, date in self.tickers:
            print(f'Running Washout Long Strategy on {symbol} on {date}')
            data = self.client.get_minute_data(symbol, date)
            trade = self.algorithim(symbol, data)
            if trade:
                self.trades.append(trade)
    
    def get_trades(self):
        return self.trades
    
    def to_csv(self, path = 'results/washoutlong/washout_long.csv'):
        # create a dataframe of the trades
        df: pd.DataFrame = pd.DataFrame(columns=['symbol', 'date', 'entry', 'stop', 'target', 'success'])
        for trade in self.trades:
            df.loc[len(df)] = [trade.symbol, trade.date, trade.entry, trade.stop, ' '.join([str(item) for item in trade.targets]), trade.success]
        df.to_csv(path, index=False)
            
            
        
        