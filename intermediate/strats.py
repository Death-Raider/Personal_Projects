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
    df.bfill(inplace=True)
    return df

def get_signal_combined(df: pd.DataFrame, thresh: list[int] = [80, 20]) -> pd.DataFrame:
    df = df.copy()
    df['signal'] = 0

    # ---- Bollinger Bands Conditions ----
    bb_buy = (
        (df['close'] < df['lower_band']) | 
        (df['close'] < df['lower_band'] - 5)
    )
    bb_sell = (
        (df['close'] > df['upper_band']) | 
        (df['close'] > df['upper_band'] - 5)
    )

    # ---- K and D Crossing Conditions ----
    kdj_buy_cross = (
        (df['kdj_k'].shift(1) < df['kdj_d'].shift(1)) &  # K was below D
        (df['kdj_k'] > df['kdj_d'])                     # K now above D
    )

    kdj_sell_cross = (
        (df['kdj_k'].shift(1) > df['kdj_d'].shift(1)) &  # K was above D
        (df['kdj_k'] < df['kdj_d'])                     # K now below D
    )

    # ---- J Crossing Threshold Conditions ----
    j_cross_up = (
        (df['kdj_j'].shift(1) < thresh[1]) &  # J was below lower threshold before (e.g., 20)
        (df['kdj_j'] > thresh[1])             # J crossed above lower threshold
    )

    j_cross_down = (
        (df['kdj_j'].shift(1) > thresh[0]) &  # J was above upper threshold before (e.g., 80)
        (df['kdj_j'] < thresh[0])             # J crossed below upper threshold
    )

    # ---- Combined Strategy ----
    df.loc[(bb_buy | (kdj_buy_cross | j_cross_up)), 'signal'] = 1    # Strong Buy
    df.loc[(bb_sell & ( kdj_sell_cross | j_cross_down)), 'signal'] = -1  # Strong Sell

    return df


def backtest(df: pd.DataFrame, hold_period: int, sl_dollars: float = None, tp_dollars: float = None):
    trades = []
    idx = 0
    in_trade = False  # Track whether a trade is active
    max_drawdown = max_drawup = 0
    while idx < len(df):
        if not in_trade:
            max_drawdown = max_drawup = 0
            signal = df.loc[idx, 'signal']
            if signal == 0:
                idx += 1
                continue

            entry_price = df.loc[idx, 'close']
            entry_time = df.loc[idx, 'time']

            # Set SL/TP prices
            sl_price = tp_price = None
            if sl_dollars is not None and tp_dollars is not None:
                sl_price = entry_price - sl_dollars if signal == 1 else entry_price + sl_dollars
                tp_price = entry_price + tp_dollars if signal == 1 else entry_price - tp_dollars

            in_trade = True  # Trade is now active
            trade_start_idx = idx
            idx += 1
            continue

        # Managing the open trade
        exit_idx = trade_start_idx + hold_period
        if idx > exit_idx or idx >= len(df):
            # Exit trade if hold period is over or data ends
            exit_price = df.loc[min(exit_idx, len(df)-1), 'close']
            exit_time = df.loc[min(exit_idx, len(df)-1), 'time']
            profit = (exit_price - entry_price) if signal == 1 else (entry_price - exit_price)
            trades.append({
                'entry_time': entry_time,
                'exit_time': exit_time,
                'signal': signal,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'profit_usd': profit,
                'max_drawdown': max_drawdown,  # Optional, can be calculated separately
                'max_drawup': max_drawup
            })
            in_trade = False
            idx = exit_idx  # Move to the next candle after exit
            continue

        # Check intratrade SL/TP
        close_price = df.loc[idx, 'close']
        if sl_price and ((signal == 1 and close_price <= sl_price) or (signal == -1 and close_price >= sl_price)):
            exit_price = sl_price
            exit_time = df.loc[idx, 'time']
            profit = (exit_price - entry_price) if signal == 1 else (entry_price - exit_price)
            trades.append({
                'entry_time': entry_time,
                'exit_time': exit_time,
                'signal': signal,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'profit_usd': profit,
                'max_drawdown': max_drawdown,
                'max_drawup': max_drawup
            })
            in_trade = False
            continue

        if tp_price and ((signal == 1 and close_price >= tp_price) or (signal == -1 and close_price <= tp_price)):
            exit_price = tp_price
            exit_time = df.loc[idx, 'time']
            profit = (exit_price - entry_price) if signal == 1 else (entry_price - exit_price)
            trades.append({
                'entry_time': entry_time,
                'exit_time': exit_time,
                'signal': signal,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'profit_usd': profit,
                'max_drawdown': max_drawdown,
                'max_drawup': max_drawup
            })
            in_trade = False
            continue
        
        max_drawdown = min(max_drawdown, (close_price - entry_price) if signal == 1 else (entry_price - close_price))
        max_drawup = max(max_drawup, (close_price - entry_price) if signal == 1 else (entry_price - close_price))
        idx += 1

    trades_df = pd.DataFrame(trades)
    trades_df['max_drawdown'] = trades_df['max_drawdown'].abs()
    trades_df['drawup_drawdown_ratio'] = trades_df['max_drawup'] /(trades_df['max_drawdown']+0.1)  # Avoid division by zero
    if len(trades_df) == 0:
        return trades_df, 0, 0
    total_profit = trades_df['profit_usd'].sum()
    win_rate = (trades_df['profit_usd'] > 0).mean()

    return trades_df, total_profit, win_rate

