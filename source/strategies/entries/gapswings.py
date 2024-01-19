from datetime import datetime, timedelta
from polygon.rest.models import Agg
from typing import List

from clients.polygon import PolygonClient
from objs.trades import Trade

class GapAndGo():
    polygon = PolygonClient()
    def algorithim(self, symbol, date: datetime):
        # using daily data starting 10 days before the gap
        data = self.polygon.get_stock_data(symbol, date - timedelta(days=20), date + timedelta(days=20))
        # find the candle matching input date
        gap_ind = None
        for i in range(len(data)):
            if datetime.fromtimestamp(data[i].timestamp / 1000).date() == date.date():
                gap_ind = i
                break
        
        # check not none
        if gap_ind == None:
            return
        
        # get maximum highs in the pass 10 days
        highs = [day.high for day in data[gap_ind-10:gap_ind]]
        max_high = max(highs)
        if data[gap_ind].close < max_high:
            return
        
        # check if gap is up and closed above previous days high
        gap = data[gap_ind]
        if not(gap.open > data[gap_ind-1].high and gap.close > data[gap_ind-1].high):
            return
            
        # look for the following sequence for the next five days - candle that has a lower high followed by a candle that breaks the lower high
        # the lower high candle must touch the 9 sma
        for i in range(gap_ind+2, gap_ind+7):
            sma9 = sum([day.close for day in data[i-10:i-1]]) / 9
            pullin = data[i-1].low < sma9
            lower_high = data[i-1].high < data[i-2].high
            break_out = data[i].high > data[i-1].high
            
            if lower_high and break_out:
                entry = data[i-1].high
                stop = data[i-1].low
                target = data[i-1].high + (entry - stop)
                target2 = data[i-1].high + 2 * (entry - stop)
                return Trade(symbol, date, [(data[i].timestamp,entry,1)], stop, [target, target2])
