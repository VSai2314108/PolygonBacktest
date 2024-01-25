import pandas as pd 
class Universe:
    """
    A class to represent a universe of stocks \n
    Can be a sector, index, or any other grouping of stocks \n
    """
    def __init__(self, path_to_tickers):
        df = pd.read_csv(path_to_tickers)
        symbols = df['Ticker'].tolist()
        self.tickers = [symbol for symbol in symbols if str(symbol).isalpha()]
    
    def get_tickers(self):
        return self.tickers
