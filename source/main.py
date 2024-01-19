from strategies.main import algorithim
from datetime import datetime

if __name__ == '__main__':
    algo = algorithim("gapandgo", "sma9", "swing_trading", "/Users/vsai23/Workspace/PolygonBacktest/tv.csv", datetime(2023, 1, 1), datetime(2023, 6, 30))
    algo.run()
    algo.to_csv()