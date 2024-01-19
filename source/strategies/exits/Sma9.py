from datetime import timedelta
from objs.trades import Trade
from clients.polygon import PolygonClient
from polygon.rest.models import Agg

from typing import List
class Sma9:
    polygon = PolygonClient()

    def evaluate(self, trade: Trade, tf):
        _, per = tf
        targets = trade.targets
        num_targs = len(targets)
        
        data = None
        if per == "min":
            # get the minute data from the first trade to the end of the day
            data: List[Agg] = self.polygon.get_minute_data(trade.symbol, trade.date)
            # drop the portion of the data before the first trade
        else: 
            # get the data for the day
            data = self.polygon.get_stock_data(trade.symbol, trade.date-timedelta(days=10), trade.date+timedelta(days=50), tf)
        
        # find the first candle after the first trade
        start_ind = None
        for i in range(len(data)):
            if data[i].timestamp > trade.trades[0][0]:
                start_ind = i
                break
        targ = 0
        for j in range(start_ind, len(data)):
            sma9 = sum([day.close for day in data[j-10:j-1]]) / 9
            if data[j].high >= targets[0]:
                    trade.add_trade((data[j].timestamp, targets[targ], -trade.remaining*0.5))
                    if data[j].high < sma9:
                        # use targets for the rest of the position
                        targ = 1
                        for k in range(j+1, len(data)):
                            if data[k].high >= targets[targ]:
                                # if the target is the last target
                                if targ == num_targs - 1:
                                    # sell the rest of the position
                                    trade.add_trade((data[k].timestamp, targets[targ], -trade.remaining))
                                    return
                                else:
                                    # sell half the position
                                    trade.add_trade((data[k].timestamp, targets[targ], -trade.remaining*0.5))
                                    targ = targ + 1
                            if data[k].low <= trade.stop:
                                # sell the rest of the position
                                trade.add_trade((data[k].timestamp, trade.stop, -trade.remaining))
                                return
                    else:
                        for k in range(j+1, len(data)):
                            sma9 = sum([day.close for day in data[k-10:k-1]]) / 9
                            if data[k].low <= sma9:
                                trade.add_trade((data[k].timestamp, data[k].low, -trade.remaining))
                                return
                        trade.add_trade((data[-1].timestamp, data[-1].close, -trade.remaining)) # if 50 days pass
                        return
            if data[j].low <= trade.stop:
                # sell the rest of the position
                trade.add_trade((data[j].timestamp, trade.stop, -trade.remaining))
                return
        # if the trade is still open at the end of the day sell it at the close
        trade.add_trade((data[-1].timestamp, data[-1].close, -trade.remaining))
        return
        
        
        
        
        
        
        
        