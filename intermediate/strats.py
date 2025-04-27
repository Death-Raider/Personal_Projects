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

def get_signal(df: pd.DataFrame, thresh: list[int] = [80,20]) -> pd.DataFrame:
    df['signal'] = 0
    df.loc[(df['close'] > df['upper_band']), 'signal'] = -1  # Sell signal
    df.loc[(df['close'] < df['lower_band']), 'signal'] = 1   # Buy signal
    df['signal'] = np.where(
        df['signal'] == 0,
        np.where(
            np.logical_and(
                (df['kdj_k'] - df['kdj_d']) > 0, 
                (df['kdj_j'] > (thresh[1] - 5)) & (df['kdj_j'] < (thresh[1] + 5))
            ), 
            1,
            np.where(
                np.logical_and(
                    (df['kdj_k'] - df['kdj_d']) < 0,
                    (df['kdj_j'] > (thresh[0] - 5)) & (df['kdj_j'] < (thresh[0] + 5))
                ), 
                -1, 
                0
            )
        ),
        df['signal']
    )
    return df