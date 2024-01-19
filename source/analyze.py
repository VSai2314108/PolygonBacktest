import pandas as pd
from datetime import datetime, timedelta
if __name__ == '__main__':
    results_file = "/Users/vsai23/Workspace/PolygonBacktest/source/results/gapandgo/sma9_2023-01-01_2023-06-30.csv"
    df = pd.read_csv(results_file)
    rs = 0
    winners = 0
    
    for current_index in range(len(df)):
        row = df.iloc[current_index]
        _,symbol,date,stop,targets,trades = row
                    
        # split the trades into a list of tuples
        trades = trades[2:-2].split('), (')
        trades = [trade.split(',') for trade in trades]
        trades = [(datetime.fromtimestamp(int(trade[0])/1000), float(trade[1]), float(trade[2])) for trade in trades]
        
        r = trades[0][1] - stop
        r = max(r, 0.01)
        
        total = 0
        # compute the r frm the rest of the trades
        for trade in trades[1:]:
            total += (trade[1] - trades[0][1])*(-trade[2])
        
        if total >= 0:
            winners += 1
        rs += total/r
    print('Average R: ' + str(rs/len(df)))
    print('Total Trades: ' + str(len(df)))
    print('Winrate: ' + str(winners/len(df)))

    