from data_fetcher import data_fetcher
from config_loader import config
from metrics_calculator import metrics_calculator

import pandas as pd
import numpy as np
import time

from backtest_engine import BacktestEngine 
from trade_visualizer import TradeVisualizer, visualize_backtest

if not data_fetcher.connect():
    raise Exception("Failed to connect to MT5")

timeframe = config.get('trading', 'active_timeframe')

m5_df = data_fetcher.fetch_data(timeframe)
m5_df = metrics_calculator.calculate_all_metrics(m5_df, timeframe)

h1_df = data_fetcher.fetch_data('H1')
h1_df = metrics_calculator.calculate_all_metrics(h1_df, 'H1')

h4_df = data_fetcher.fetch_data('H4')
h4_df = metrics_calculator.calculate_all_metrics(h4_df, 'H4')

engine = BacktestEngine()
trades, equity = engine.run_backtest(
    m5_df, 'M5',
    use_mtf=True,
    h1_df=h1_df,
    h4_df=h4_df
)

# visualize_backtest(m5_df, trades, timeframe)