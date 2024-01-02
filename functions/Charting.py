from httpx import get
from matplotlib.pyplot import fill_between, savefig
import pandas as pd
import mplfinance as mpf
from datetime import datetime, time
import os
from datetime import datetime, timedelta
from numpy import poly
from polygon.rest import RESTClient
from polygon.rest.models import Agg
from typing import List
from .PolygonClient import PolygonClient

class Charts:
    def __init__(self, client: PolygonClient):
        self.client: PolygonClient = client
        
    def plot_ohlc_chart_min(self, stock, date, tf, save = False, hlines = None, dir ='data'):
        # pull data
        if tf == "M":
            data: List[Agg] = self.client.get_minute_data(stock, date)
        else:
            data: List[Agg] = self.client.get_day_data(stock, date)
        # Parse and organize data into a DataFrame
        parsed_data = {
            'Date': [datetime.fromtimestamp(item.timestamp / 1000) for item in data],
            'Open': [item.open for item in data],
            'High': [item.high for item in data],
            'Low': [item.low for item in data],
            'Close': [item.close for item in data],
            'Volume': [item.volume for item in data],
            'VWAP': [item.vwap for item in data]
        }

        df = pd.DataFrame(parsed_data)
        df.set_index('Date', inplace=True)
            
        # Calculate EMAs
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        # Calculate SMAs
        df['SMA_9'] = df['Close'].rolling(window=9).mean()
        df['SMA_21'] = df['Close'].rolling(window=21).mean()
            
        if tf == "M":
            # Calculate VWAP using OHLC and Volume
            df['typical_price'] = (df['High'] + df['Low'] + df['Close']) / 3

            # Calculate the product of typical price and volume
            df['tp_volume'] = df['typical_price'] * df['Volume']

            # Calculate the cumulative sum of tp_volume and the cumulative sum of volume
            df['cumulative_tp_volume'] = df['tp_volume'].cumsum()
            df['cumulative_volume'] = df['Volume'].cumsum()

            # Calculate VWAP
            df['VWAP'] = df['cumulative_tp_volume'] / df['cumulative_volume']

            # Drop the intermediate columns if they are not needed
            df.drop(['typical_price', 'tp_volume', 'cumulative_tp_volume', 'cumulative_volume'], axis=1, inplace=True)
            
            # Create additional plots for VWAP and EMAs
            apds = [
                mpf.make_addplot(df['VWAP'], color='purple', width=0.7),
                # mpf.make_addplot(df['EMA_9'], color='blue', width=0.7),
                # mpf.make_addplot(df['EMA_21'], color='red', width=0.7)
                mpf.make_addplot(df['SMA_9'], color='blue', width=0.7),
                mpf.make_addplot(df['SMA_21'], color='red', width=0.7)
            ]
            
            df['Pre930'] = [True if minute.time() < time(9, 30) else False for minute in df.index]
            
            if save:
                # check if directory /data/{date}
                if not os.path.exists(f"./{dir}/{date}/{stock}"):
                    os.makedirs(f"./{dir}/{date}/{stock}")
                
                if hlines != None:
                    mpf.plot(df, 
                        type='candle', volume=True, addplot=apds, style='charles', title='OHLC Chart with Volume', ylabel='Price', 
                        fill_between=dict(y1=max(df['Low']), y2=min(df['High']), where=df['Pre930'], alpha=0.2, color='gray'),
                        hlines= (dict(hlines=hlines[0], colors = hlines[1])),
                        figsize = (48,27), savefig=dict(fname = f"./{dir}/{date}/{stock}/{stock}-{tf}.png", dpi=400), returnfig=True)
                else:
                    mpf.plot(df, 
                            type='candle', volume=True, addplot=apds, style='charles', title='OHLC Chart with Volume', ylabel='Price', 
                            fill_between=dict(y1=max(df['Low']), y2=min(df['High']), where=df['Pre930'], alpha=0.2, color='gray'),
                            figsize = (48,27), savefig=dict(fname = f"./{dir}/{date}/{stock}/{stock}-{tf}.png", dpi=400), returnfig=True)
            else:
                if hlines != None:
                    return mpf.plot(df, 
                        type='candle', volume=True, addplot=apds, style='charles', title='OHLC Chart with Volume', ylabel='Price', 
                        fill_between=dict(y1=max(df['Low']), y2=min(df['High']), where=df['Pre930'], alpha=0.2, color='gray'),
                        hlines= (dict(hlines=hlines[0], colors = hlines[1])),
                        figsize = (18,12), returnfig=True)
                else:
                    return mpf.plot(df, 
                            type='candle', volume=True, addplot=apds, style='charles', title='OHLC Chart with Volume', ylabel='Price', 
                            fill_between=dict(y1=max(df['Low']), y2=min(df['High']), where=df['Pre930'], alpha=0.2, color='gray'),
                            figsize = (18,12), returnfig=True)

        else:
            df.drop(['VWAP'], axis=1, inplace=True)
            
            # Create additional plots for EMAs
            apds = [
                mpf.make_addplot(df['EMA_9'], color='blue', width=0.7),
                mpf.make_addplot(df['EMA_21'], color='red', width=0.7)
            ]
        
            if save:
                # check if directory /data/{date}
                if not os.path.exists(f"./data/{date}/{stock}"):
                    os.makedirs(f"./data/{date}/{stock}")
                
                # save chart
                mpf.plot(df, type='candle', volume=True, addplot=apds, style='charles', 
                        title=f"{stock}-{date}-{tf}", ylabel='Price', 
                        savefig=dict(fname = f"./data/{date}/{stock}/{stock}-{tf}.png", dpi=400))
            else:
                mpf.plot(df, type='candle', volume=True, addplot=apds, style='charles', title='OHLC Chart with Volume', ylabel='Price')