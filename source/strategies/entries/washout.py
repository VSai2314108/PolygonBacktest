from typing import List
from polygon.rest.models import Agg
from datetime import date, datetime, time, timedelta
import pandas as pd

from clients.polygon import PolygonClient
from objs.trades import Trade

class WashoutLong():
    polygon = PolygonClient()
    
    def algorithim(self, symbol, date):
        # pull the dataframes needed
        data = self.polygon.get_minute_data(symbol, date)
        
        # find the index of the first candle with a timestamp >= 9:30
        ninethirty = None
        stop = None
        entry = None
        for i in range(len(data)):
            if datetime.fromtimestamp(data[i].timestamp / 1000).time() >= time(9, 30):
                ninethirty = i
                break
        
        i = i+1 # increment i to the next candle
        
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
            entry = data[i].high
            i = i + 1
        
        # entry and target
        stop = min(data[i-1].low, stop)
        entry = min(entry, data[i-1].high)
        target = entry + (entry - stop)
        target2 = entry + (entry - stop) * 2 # for later use if we want to proceed to two r
        
        trades = []
        trades.append((data[i].timestamp, data[i-1].high, 1))
        return Trade(symbol, date, trades, stop, [target, target2])
            
            
        
        