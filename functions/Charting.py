from httpx import get
from matplotlib.pyplot import fill_between, savefig
import pandas as pd
import mplfinance as mpf
from datetime import datetime, time
import os
from datetime import datetime, timedelta
from numpy import NaN, poly
from polygon.rest import RESTClient
from polygon.rest.models import Agg
from typing import List
from .PolygonClient import PolygonClient
import numpy as np

class Charts:
    def __init__(self, client: PolygonClient):
        self.client: PolygonClient = client
    
    def plot(self, symbol, date, tf, hlines=None, vlines=None, fills=None, save=False, backoff: timedelta=timedelta(days=0), forwardoff: timedelta=timedelta(days=0)):
        """
        symbol: str -> stock symbol
        data: List[Agg] -> list of polygon rest models
        hlines: List[(str, str)] -> list of horizontal lines and color
        vlines: List[(str, str)] -> list of vertical lines and color
        fills: List[(int, int, str)] -> list of start time stampe end timestamp and color
        """
        # create start and end date using backoof and forwardoff - assume date is a string down to the second
        start_date = date - backoff
        end_date = date + forwardoff
        
        data: List[Agg] = self.client.get_stock_data(symbol, start_date, end_date, tf)
        
        timeframe = (data[-1].timestamp - data[0].timestamp) / 1000 / 60 / len(data)

        # parse input
        parsed_data = {
            'Date': [datetime.fromtimestamp(item.timestamp / 1000) for item in data],
            'Open': [item.open for item in data],
            'High': [item.high for item in data],
            'Low': [item.low for item in data],
            'Close': [item.close for item in data],
            'Volume': [item.volume for item in data],
            'VWAP': [item.vwap for item in data],
        }
        
        # create data fram with Date as index
        data = pd.DataFrame(parsed_data, index=parsed_data['Date'])
        
        # if time frame is less than a day set boolean lower to true
        if timeframe < 1440:
            lower = True
        else:
            lower = False
            
        # add column for vwap if time frame is less than a day
        if lower:
            # Calculate VWAP using OHLC and Volume
            data['typical_price'] = (data['high'] + data['low'] + data['close']) / 3

            # Calculate the product of typical price and volume
            data['tp_volume'] = data['typical_price'] * data['volume']

            # Calculate the cumulative sum of tp_volume and the cumulative sum of volume
            data['cumulative_tp_volume'] = data['tp_volume'].cumsum()
            data['cumulative_volume'] = data['volume'].cumsum()

            # Calculate VWAP
            data['VWAP'] = data['cumulative_tp_volume'] / data['cumulative_volume']

            # Drop the intermediate columns if they are not needed
            data.drop(['typical_price', 'tp_volume', 'cumulative_tp_volume', 'cumulative_volume'], axis=1, inplace=True)
            
            # add pre 9:30 boolean
            data['Pre930'] = [True if minute.time() < time(9, 30) else False for minute in data.index]

        # Calculate SMAs
        data['SMA_9'] = data['Close'].rolling(window=9).mean()
        data['SMA_21'] = data['Close'].rolling(window=21).mean()
        
        # create additional plots with sma
        apds = [mpf.make_addplot(data['SMA_9'], color='blue', width=0.7),
                mpf.make_addplot(data['SMA_21'], color='red', width=0.7)]
        
        # create a column call data['vline'] and set the dates included in vlines to true and the rest to false
        if vlines != None:
            vline = [True if minute in vlines[0] else False for minute in data.index]
            # create a pd series with close price if true if not 0
            data['vline'] = [data['Low'][i] if vline[i] else min(data['Close']) for i in range(len(vline))]

            # create a scatter plot for vlines with black triangles
            apds.append(mpf.make_addplot(data['vline'], type='scatter', marker='^', markersize=100, color='black'))
            
            
        # if lower add vwap
        if lower:
            apds.append(mpf.make_addplot(data['VWAP'], color='purple', width=0.7))
        
        # create kwargs for mpf.plot
        plot_params = {
            'type': 'candle',
            'volume': True,
            'addplot': apds,  # Ensure 'apds' is defined elsewhere in your code
            'style': 'charles',
            'title': 'OHLC Chart with Volume',
            'ylabel': 'Price',
            'figsize': (48,27),
            'returnfig': True
        }
        
        if lower:
            plot_params['fill_between'] = dict(y1=max(data['low']), y2=min(data['high']), where=data['Pre930'], alpha=0.2, color='gray')
        if hlines != None:
            plot_params['hlines'] = (dict(hlines=hlines[0], colors = hlines[1]))
        if save:
            plot_params['savefig'] = dict(fname = f"./{dir}/{date}/{symbol}/{symbol}-{'Min' if lower else 'Day'}.png", dpi=400)
        
        # plot
        return mpf.plot(data, **plot_params)        
        
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
            apds = [
                # mpf.make_addplot(df['EMA_9'], color='blue', width=0.7),
                # mpf.make_addplot(df['EMA_21'], color='red', width=0.7)
                mpf.make_addplot(df['SMA_9'], color='blue', width=0.7),
                mpf.make_addplot(df['SMA_21'], color='red', width=0.7)
            ]
            
            
            if save:
                # check if directory /data/{date}
                if not os.path.exists(f"./{dir}/{date}/{stock}"):
                    os.makedirs(f"./{dir}/{date}/{stock}")
                
                if hlines != None:
                    mpf.plot(df, 
                        type='candle', volume=True, addplot=apds, style='charles', title='OHLC Chart with Volume', ylabel='Price',
                        hlines= (dict(hlines=hlines[0], colors = hlines[1])),
                        figsize = (48,27), savefig=dict(fname = f"./{dir}/{date}/{stock}/{stock}-{tf}.png", dpi=400), returnfig=True)
                else:
                    mpf.plot(df, 
                            type='candle', volume=True, addplot=apds, style='charles', title='OHLC Chart with Volume', ylabel='Price', 
                            figsize = (48,27), savefig=dict(fname = f"./{dir}/{date}/{stock}/{stock}-{tf}.png", dpi=400), returnfig=True)
            else:
                if hlines != None:
                    return mpf.plot(df, 
                        type='candle', volume=True, addplot=apds, style='charles', title='OHLC Chart with Volume', ylabel='Price', 
                        hlines= (dict(hlines=hlines[0], colors = hlines[1])),
                        figsize = (18,12), returnfig=True)
                else:
                    return mpf.plot(df, 
                            type='candle', volume=True, addplot=apds, style='charles', title='OHLC Chart with Volume', ylabel='Price', 
                            figsize = (18,12), returnfig=True)
