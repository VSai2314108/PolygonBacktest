from multiprocessing import freeze_support
from matplotlib.patches import Polygon
from numpy import inner
import pandas as pd
from polygonchart import PolygonChart

from polygon.rest.models import Agg
from typing import List
from datetime import datetime
import os

if __name__ == "__main__":
    def on_row_click(row):
        date = row['date']
        symbol = row['Symbol']
        trades = row['trades']
        targets = row['targets']
        
        # remove the brackets and split on commas and conver targets to list of floats
        targets = targets[1:-1].split(',')
        targets = [float(target) for target in targets]
                    
        # split the trades into a list of tuples
        trades = trades[2:-2].split('), (')
        trades = [trade.split(',') for trade in trades]
        trades = [(datetime.fromtimestamp(int(trade[0])/1000), float(trade[1]), float(trade[2])) for trade in trades]
        
        chart.end_date = date.split(' ')[0]
        chart.run_script(f'''
            {chart.id}.search.window.style.display = "flex"
            {chart.id}.search.box.focus()
            {chart.id}.search.box.value = "{symbol}"
        ''')
        
        # add markers for the trades
        for trade in trades:
            chart.marker(trade[0], 
                         'above' if trade[2] < 0 else 'below', 
                         'arrow_down' if trade[2] < 0 else 'arrow_up',
                         'r' if trade[2] < 0 else 'g')
        # {chart.id}.search.box.dispatchEvent(new KeyboardEvent('keydown', {{key: 'Enter', code: 'Enter',which: 13, keyCode: 13,}});

        chart.show(block=True)
       
    chart = PolygonChart(
        api_key="_P_Tx1Fp5qmdMSa0v9sFsgOp014W2cEa", width=1000, inner_width=0.7, inner_height=1)
    
    # table = chart.create_table(width=0.3, height=1,
    #               headings=('Symbol', 'date', 'stop', 'targets', 'trades'),
    #               widths=(0.2, 0.1, 0.2, 0.2, 0.3),
    #               alignments=('center', 'center', 'right', 'right', 'right'),
    #               position='left', func=on_row_click)
    
    # file_path = "/Users/vsai23/Workspace/PolygonBacktest/source/results/gapandgo/sma9_2023-01-01_2023-06-30.csv"
    # if file_path:
    #     # csv format: index, symbol, date, stop, targets, trades
    #     df = pd.read_csv(file_path)
    #     current_index = 0
        
    #     # sort the df by row date
    #     df['date'] = pd.to_datetime(df['date'])
    #     df = df.sort_values(by=['date'])
    #     df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
    #     # populate the table
    #     for index, row in df.iterrows():
    #         _,symbol,date,stop,targets,trades = row   
    #         table.new_row(symbol, date, stop, targets, trades)
            
    # table.footer(2)
    # table.footer[0] = 'Selected:'
    
    chart.show(block=True)