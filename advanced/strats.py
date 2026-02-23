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
df = data_fetcher.fetch_data(timeframe)
df = metrics_calculator.calculate_all_metrics(df, timeframe)

engine = BacktestEngine()
trades, equity = engine.run_backtest(df, timeframe)

print(trades)
print(equity)

visualize_backtest(df, trades, timeframe)