import datetime
from functions.Universe import Universe
from functions.PolygonClient import PolygonClient
from functions.Scanners import Scanners
from functions.WashoutLong import WashoutLong
from functions.GapAndGo import GapAndGo
import pandas as pd
from functions.Charting import Charts
import os

def main():
    # Create a Universe
    universe = Universe('tv.csv')
    
    # Create a Polygon client
    polygon_client = PolygonClient(os.environ.get('POLYGON_API_KEY'))

    # Create a Scanner
    scanner = Scanners(polygon_client, universe, 'swing_trading')

    # Invoke the washout long strategy
    strategy = GapAndGo(scanner, polygon_client)
    strategy.evaluate()
    
    # Get the trades
    trades = strategy.get_trades()
    
    # save to csv
    strategy.to_csv()

    # Return the list of trades
    return trades

if __name__ == "__main__":
    main()
    df = pd.read_csv('results/GapAndGoSwing/gg.csv')
    
    # count success vs failure
    print(f"Total Trades: {len(df)}")
    print(f"Total R: {df['success'].sum()}")
    print(f"R per trade: {df['success'].sum() / len(df)}")
    print(f"Percent Loss Trades: {len(df[df['success'] == 'True']) / len(df)}")
    
    # chart = Charts(PolygonClient(os.environ.get('POLYGON_API_KEY')))
    # os.environ.setdefault('strategy', 'GapAndGo')
    # fig, _ = chart.plot('AAPL', datetime.date(2021, 1, 1), (1, 'day'), backoff=datetime.timedelta(days=50), forwardoff=datetime.timedelta(days=50))
    
    
    
