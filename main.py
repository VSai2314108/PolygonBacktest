from matplotlib.pyplot import sca
from functions.Universe import Universe
from functions.PolygonClient import PolygonClient
from functions.Scanners import Scanners
from functions.WashoutLong import WashoutLong
import pandas as pd
import os

def main():
    # Create a Universe
    universe = Universe('tv.csv')
    
    # Create a Polygon client
    polygon_client = PolygonClient(os.environ.get('POLYGON_API_KEY'))

    # Create a Scanner
    scanner = Scanners(polygon_client, universe, 'gap_trading')

    # Invoke the washout long strategy
    strategy = WashoutLong(scanner, polygon_client)
    strategy.evaluate()
    
    # Get the trades
    trades = strategy.get_trades()
    
    # save to csv
    strategy.to_csv()

    # Return the list of trades
    return trades

if __name__ == "__main__":
    df = pd.read_csv('results/washout_long.csv')
    
    # count success vs failure
    print(f"Total R: {df['success'].sum()}")
    print(f"R per trade: {df['success'].sum() / len(df)}")
    print(f"Percent Loss Trades: {len(df[df['success'] < 0]) / len(df)}")
    
    
    
