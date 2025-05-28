import pandas as pd
import numpy as np
# from latest_trader import execute_trade, close_trade, update_tp_sl, get_adaptive_sl_tp
import MetaTrader5 as mt5

def get_latest_data(symbol=1, timeframe=2, newest=False):
    count=10
    new_count = 10
    df = pd.DataFrame({
        "time": pd.date_range(start="2023-01-01", periods=count, freq='T'),
        "open": np.random.rand(count) * 1000,
        "high": np.random.rand(count) * 1000 + 10,
        "low": np.random.rand(count) * 1000 - 10,
        "close": np.random.rand(count) * 1000,
        "tick_volume": np.random.randint(1, 100, count),
    })
    new_start_date = df.iloc[-5]['time']
    
    new_df = pd.DataFrame({
        "time": pd.date_range(start=new_start_date, periods=new_count, freq='T'),
        "open": np.random.rand(count) * 1000,
        "high": np.random.rand(count) * 1000 + 10,
        "low": np.random.rand(count) * 1000 - 10,
        "close": np.random.rand(count) * 1000,
        "tick_volume": np.random.randint(1, 100, count),
    })
    return df, new_df

def initilize_df(symbol, timeframe, count):
    df,_ = get_latest_data(symbol, timeframe, count=count)
    # df = bollbands(df, period=20)
    # df = KDJ(df, period=14, k_smooth=3, d_smooth=10)
    bias_df = None
    # bias_df = get_latest_data(symbol, timeframe, count=count)
    # bias_df = get_bias(df, period=200)
    # df = get_signal_combined(df, thresh=[80, 30], bias=bias_df.loc['bias'])
    return df, bias_df

def update_df(symbol:str, timeframe:int, df:pd.DataFrame, bias_df:pd.DataFrame, count=100):
    _,latest_df = get_latest_data(symbol, timeframe)
    print(latest_df)
    if latest_df.empty:
        print("No new data available.")
        return df, bias_df

    # Append latest data to df based on time, and update the rows with the same times to the ones from the latest_df
    # mask = df['time'].isin(latest_df['time']) # Check if time exists in df
    # print(mask)
    # print(df[mask])
    # print(latest_df[~mask])
    # print(latest_df[mask])
    # df[mask] = latest_df[~mask].values # Update existing rows
    df = pd.concat([df, latest_df], ignore_index=True).drop_duplicates(ignore_index=True, subset=['time'], keep='last') # Append new rows
    bias_df = None
    df.reset_index(inplace=True)

    return df, bias_df

import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
DEMO_ACCOUNT_NO = 10820447
DEMO_ACCOUNT_PASS = "eK!K5l#d"
# establish MetaTrader 5 connection to a specified trading account
if not mt5.initialize(login=DEMO_ACCOUNT_NO, server="VantageInternational-Demo",password=DEMO_ACCOUNT_PASS):
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# display data on connection status, server name and trading account
print(mt5.terminal_info())
# display data on MetaTrader 5 version
print(mt5.version())
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()