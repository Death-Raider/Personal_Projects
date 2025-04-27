import pandas as pd
import numpy as np

def KDJ(df: pd.DataFrame,period: int = 14,k_smooth: int = 3,d_smooth: int = 3) -> pd.DataFrame:
    low_min = df['low'].rolling(window=period, min_periods=1).min()
    high_max = df['high'].rolling(window=period, min_periods=1).max()
    rsv = (df['close'] - low_min) / (high_max - low_min + 1e-9) * 100
    k = rsv.ewm(span=k_smooth, adjust=False).mean()
    d = k.ewm(span=d_smooth, adjust=False).mean()
    j = 3 * k - 2 * d
    df['kdj_k'] = k
    df['kdj_d'] = d
    df['kdj_j'] = j
    return df

def bollbands(df: pd.DataFrame, period: int):
    df['middle_band'] = df['close'].rolling(window=period).mean()
    df['std_dev'] = df['close'].rolling(window=period).std()
    df['upper_band'] = df['middle_band'] + (2 * df['std_dev'])
    df['lower_band'] = df['middle_band'] - (2 * df['std_dev'])
    df.fillna(method='bfill', inplace=True)
    return df

def get_signal_combined(df: pd.DataFrame, thresh: list[int] = [80, 20]) -> pd.DataFrame:
    df = df.copy()  # avoid modifying original
    df['signal'] = 0

    # Conditions for Bollinger Bands
    bb_sell = df['close'] > df['upper_band']
    bb_buy = df['close'] < df['lower_band']

    # Conditions for KDJ
    kdj_buy = (
        (df['kdj_k'] > df['kdj_d']) &
        (df['kdj_j'] > (thresh[1] - 5)) &
        (df['kdj_j'] < (thresh[1] + 5))
    )
    kdj_sell = (
        (df['kdj_k'] < df['kdj_d']) &
        (df['kdj_j'] > (thresh[0] - 5)) &
        (df['kdj_j'] < (thresh[0] + 5))
    )

    # Combined Signal
    df.loc[bb_sell & kdj_sell, 'signal'] = -1  # Sell only if BOTH BB & KDJ say sell
    df.loc[bb_buy | kdj_buy, 'signal'] = 1     # Buy only if BOTH BB & KDJ say buy

    return df

def backtest(df: pd.DataFrame, hold_period) -> pd.DataFrame:
    trades = []

    for idx, row in df.iterrows():
        signal = row['signal']
        if signal == 0:
            continue
        
        entry_price = row['close']
        entry_time = row['time']
        
        # Find exit candle
        exit_idx = idx + hold_period
        if exit_idx >= len(df):
            break

        exit_price = df.loc[exit_idx, 'close']
        exit_time = df.loc[exit_idx, 'time']

        # Calculate PnL
        if signal == 1:  # Buy
            profit = (exit_price - entry_price)
        elif signal == -1:  # Sell
            profit = (entry_price - exit_price)

        trades.append({
            'entry_time': entry_time,
            'exit_time': exit_time,
            'signal': signal,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'profit_usd': profit
        })

    # Create a trades DataFrame
    trades_df = pd.DataFrame(trades)

    # Results
    total_profit = trades_df['profit_usd'].sum()
    win_rate = (trades_df['profit_usd'] > 0).mean()

    return trades_df, total_profit, win_rate