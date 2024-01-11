import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFileDialog, QListWidget, QSplitter
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import mplfinance as mpf
import os

from clients.polygon import PolygonClient
from graphics.charting import Charts

from datetime import datetime, timedelta     
class StockApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_index = 0
        self.df = None
        self.charts = Charts(PolygonClient())

        # Main Widget
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        # Horizontal layout for list and chart
        self.h_layout = QHBoxLayout(self.main_widget)
        
        # List Widget
        self.list_widget = QListWidget()
        self.list_widget.setFixedSize(200, 900)
        self.h_layout.addWidget(self.list_widget)
        self.list_widget.itemClicked.connect(self.on_list_item_clicked)

        # Vertical Layout for Chart and Controls
        self.v_layout = QVBoxLayout()
        self.h_layout.addLayout(self.v_layout)

        # Matplotlib Figure and Canvas
        self.figure: Figure = Figure()
        self.canvas: FigureCanvas = FigureCanvas(self.figure)
        self.canvas.setFixedSize(1200, 800)
        self.v_layout.addWidget(self.canvas)

        # Upload Button
        self.upload_button = QPushButton("Upload CSV", self)
        self.upload_button.clicked.connect(self.upload_csv)
        self.v_layout.addWidget(self.upload_button)

        # Info Label
        self.info_label = QLabel("", self)
        self.v_layout.addWidget(self.info_label)

        # Navigation Buttons
        self.prev_button = QPushButton("Previous", self)
        self.prev_button.clicked.connect(self.show_previous)
        self.v_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next", self)
        self.next_button.clicked.connect(self.show_next)
        self.v_layout.addWidget(self.next_button)

        # Set the window size
        self.resizeEvent = self.on_resize
        
        # map of strategy chart offsets
        self.offsets = {
            'gapandgo': (timedelta(days=50), timedelta(days=50), (1, 'day')),
            'washout': (timedelta(minutes=300), timedelta(minutes=240), (1, 'minute'))
        }

    def upload_csv(self):
        file_path = "/Users/vsai23/Workspace/PolygonBacktest/source/results/washout/target_2023-01-01_2023-06-30.csv"
        # file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if file_path:
            # parse the second to parent folder name as the strategy
            strategy = file_path.split('/')[-2]
            os.environ['strategy'] = strategy

            self.df = pd.read_csv(file_path)
            self.current_index = 0
            
            # sort the df by row date
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df = self.df.sort_values(by=['date'])
            self.df['date'] = self.df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            self.populate_list()
            self.display_stock()

    def populate_list(self):
        self.list_widget.clear()
        for index, row in self.df.iterrows():
            self.list_widget.addItem(f"{row['symbol']} - {row['date']}")

    def on_list_item_clicked(self, item):
        # Find the index of the clicked item
        for index, row in self.df.iterrows():
            if item.text() == f"{row['symbol']} - {row['date']}":
                self.current_index = index
                break
        self.display_stock()

    def display_stock(self):
        if self.df is not None and not self.df.empty:
            row = self.df.iloc[self.current_index]
            _,symbol,date,stop,targets,trades = row
            
            # parse date
            date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            
            # remove the brackets and split on commas and conver targets to list of floats
            targets = targets[1:-1].split(',')
            targets = [float(target) for target in targets]
                        
            # split the trades into a list of tuples
            trades = trades[2:-2].split('), (')
            trades = [trade.split(',') for trade in trades]
            trades = [(datetime.fromtimestamp(int(trade[0])/1000), float(trade[1]), float(trade[2])) for trade in trades]
            
            # Convert date to datetime and extract just the date and convert it back to string
            self.info_label.setText(f"Symbol: {symbol}, Date: {date}")

            plt.close('all')
            
            hlines = [[trades[0][1], stop] + targets, ['b', 'r'] + ['g'] * len(targets)]
            
            # convert the timestamps of the trades to dates
            trades = [trade[0] for trade in trades]
            vlines = [trades, ['black']]
            
            # read in the strategy from the environment variable
            strategy = os.environ.get('strategy')
            backoff, forwardoff, tf = self.offsets[strategy]
            
            # Fetch stock data and plot
            fig, _ = self.charts.plot(symbol, date, tf, hlines=hlines, vlines=vlines, backoff=backoff, forwardoff=forwardoff)

            # Get the size of the canvas in pixels
            width, height = self.canvas.get_width_height(physical=True)
            # Convert size from pixels to inches based on the DPI
            dpi = fig.dpi
            fig.set_size_inches(width / dpi, height / dpi)

            # Draw the mplfinance figure onto the canvas
            # This method may vary depending on how your Charts class is implemented
            # Typically, you might use fig.axes[0] to access the Axes and redraw it
            self.canvas.figure = fig
            self.canvas.draw()

    def on_resize(self, event):
        # Call the superclass method
        super(StockApp, self).resizeEvent(event)
        

    def show_next(self):
        if self.df is not None and not self.df.empty:
            self.current_index = (self.current_index + 1) % len(self.df)
            self.display_stock()

    def show_previous(self):
        if self.df is not None and not self.df.empty:
            self.current_index = (self.current_index - 1) % len(self.df)
            self.display_stock()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = StockApp()
    mainWin.show()
    sys.exit(app.exec_())
