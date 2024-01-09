# Efficient backtesting for day traders in python 

## Environment setup
Python3 is a prerequisite
requirements are shown in 

## GUI
python3 gui.py opens up the viewer
choose a results file of your choice to navigate through the trades

## Workflow

### Universe Creation
Choose a stock exhange NYSE/NASDAQ etc and a time frame for which we are back testing\
Retrieve data for the higher time period (daily)

### Scanner
Find the days for which each ticker in the universe is tradeable by your criteria

### Strategy
Evaluate the strategies you use on the outputs of scanner
Save each trade as a chart file or simply as a set of trades
Day trading algorithms should set the date as 9:30 of the day while swing trading should have the date with no time 
