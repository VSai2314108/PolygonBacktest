from strategies.algo import algo
from datetime import datetime
import sys

if __name__ == "__main__":
    file = open('output.txt', 'w')
    sys.stdout = file 
      
    alg = algo("ep", "targets", datetime(2014, 1, 1), datetime(2024, 1, 1))
    alg.to_csv()