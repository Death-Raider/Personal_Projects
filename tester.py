import pandas as pd
import numpy as np

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

old, new = get_latest_data()
print(old)

old, _ = update_df('x', 0, old, None, 100)

print(old)