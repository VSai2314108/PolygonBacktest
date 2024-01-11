from datetime import timedelta
from objs.trades import Trade
from clients.polygon import PolygonClient
from polygon.rest.models import Agg

from typing import List
class Target:
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
            data = [elem for elem in data if elem.timestamp > trade.trades[0][0]]
        else: 
            # get the data for the day
            data = self.polygon.get_stock_data(trade.symbol, trade.date+timedelta(days=1), trade.date+timedelta(days=50), self.tf)
            data = [elem for elem in data if elem.timestamp > trade.trades[0][0]]
        
        # sell half at the first target and half there after and close the position at the last target
        targ = 0
        for j in range(len(data)):
            if data[j].high >= targets[targ]:
                # if the target is the last target
                if targ == num_targs - 1:
                    # sell the rest of the position
                    trade.add_trade((data[j].timestamp, targets[targ], -trade.remaining))
                    return
                else:
                    # sell half the position
                    trade.add_trade((data[j].timestamp, targets[targ], -trade.remaining*0.5))
                    targ = targ + 1
            if data[j].low <= trade.stop:
                # sell the rest of the position
                trade.add_trade((data[j].timestamp, trade.stop, -trade.remaining))
                return
        # if the trade is still open at the end of the day sell it at the close
        trade.add_trade((data[-1].timestamp, data[-1].close, -trade.remaining))
        
        
        
        
        
        
        
        