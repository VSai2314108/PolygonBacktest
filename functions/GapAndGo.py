from typing import List
from polygon.rest.models import Agg
from datetime import date, datetime, timedelta
import pandas as pd

from .Strategy import Strategy
from .Trades import Trade
from .Scanners import Scanners
from .PolygonClient import PolygonClient

class GapAndGo(Strategy):
    def __init__(self, scanner: Scanners, client: PolygonClient):
        self.client: PolygonClient = client
        self.tickers: List[tuple] = scanner.run_scanner(date(2023, 1, 1), date(2023, 12, 31))
        self.trades: List[Trade] = []
    
    def algorithim(self, symbol, data: List[Agg]):
        # using daily data starting 10 days before the gap
        
        # ensure we closed above the high of the day before the gap
        gap = data[10]
        if gap.close < data[9].high:
            return
        
        # look for the following sequence for the next five days - candle that has a lower high followed by a candle that breaks the lower high
        # the lower high candle must touch the 9 sma
        for i in range(11, 16):
            sma9 = sum([day.close for day in data[i-10:i-1]]) / 9
            pullin = data[i-1].low < sma9
            lower_high = data[i-1].high < data[i-2].high
            break_out = data[i].high > data[i-1].high
            
            if pullin and lower_high and break_out:
                entry = data[i-1].high
                stop = data[i-1].low
                target = data[i-1].high + (entry - stop)
            
                # check if the target is hit
                for j in range(i+1, len(data)):
                    if data[j].high > target:
                        return Trade(symbol, datetime.fromtimestamp(gap.timestamp / 1000).strftime('%Y-%m-%d'), entry, stop, [target], True)
                    if data[j].low < stop:
                        return Trade(symbol, datetime.fromtimestamp(gap.timestamp / 1000).strftime('%Y-%m-%d'), entry, stop, [target], False)

    
    def evaluate(self):
        for symbol, date in self.tickers:
            print(f'Running Gap And Go Swing on {symbol} with gap on {date}')
            # get the data
            data = self.client.get_stock_data(symbol, datetime.strptime(date, '%Y-%m-%d') - timedelta(days=10), datetime.strptime(date, '%Y-%m-%d') + timedelta(days=100))
            try:
                trade = self.algorithim(symbol, data)
                if trade:
                    self.trades.append(trade)
            except Exception as e:
                print(e)
                continue
    
    def get_trades(self):
        return self.trades
    
    def to_csv(self, path = 'results/GapAndGoSwing/gg.csv'):
        # create a dataframe of the trades
        df: pd.DataFrame = pd.DataFrame(columns=['symbol', 'date', 'entry', 'stop', 'target', 'success'])
        for trade in self.trades:
            df.loc[len(df)] = [trade.symbol, trade.date, trade.entry, trade.stop, ' '.join([str(item) for item in trade.targets]), trade.success]
        df.to_csv(path, index=False)
            
            
        
        