from multiprocessing import freeze_support
from matplotlib.patches import Polygon
from numpy import inner
import pandas as pd
from polygonchart import PolygonBacktestingChart

if __name__ == "__main__":
       
    chart = PolygonBacktestingChart(
        api_key="_P_Tx1Fp5qmdMSa0v9sFsgOp014W2cEa", width=1000, inner_width=0.7, inner_height=1)
    
    chart.show(block=True)