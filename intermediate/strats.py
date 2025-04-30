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
    in_trade = False
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
                if signal == 1:
                    sl_price = entry_price - sl_dollars
                    tp_price = entry_price + tp_dollars
                else:
                    sl_price = entry_price + sl_dollars
                    tp_price = entry_price - tp_dollars

            in_trade = True
            trade_start_idx = idx
            idx += 1
            continue

        # Determine trade exit point
        exit_idx = trade_start_idx + hold_period
        if idx > exit_idx or idx >= len(df):
            exit_idx = min(exit_idx, len(df) - 1)
            exit_price = df.loc[exit_idx, 'close']
            exit_time = df.loc[exit_idx, 'time']
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
            idx = exit_idx
            continue

        # Check for SL/TP hit during the trade
        close_price = df.loc[idx, 'close']

        hit_sl = sl_price is not None and (
            (signal == 1 and close_price <= sl_price) or
            (signal == -1 and close_price >= sl_price)
        )
        hit_tp = tp_price is not None and (
            (signal == 1 and close_price >= tp_price) or
            (signal == -1 and close_price <= tp_price)
        )

        if hit_sl or hit_tp:
            exit_price = sl_price if hit_sl else tp_price
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
            idx += 1
            continue

        # Track drawdown and drawup
        draw_value = close_price - entry_price if signal == 1 else entry_price - close_price
        max_drawdown = min(max_drawdown, draw_value)
        max_drawup = max(max_drawup, draw_value)

        idx += 1

    # Compile results
    trades_df = pd.DataFrame(trades)
    if not trades_df.empty:
        trades_df['max_drawdown'] = trades_df['max_drawdown'].abs()
        trades_df['drawup_drawdown_ratio'] = trades_df['max_drawup'] / (trades_df['max_drawdown'] + 0.1)
        total_profit = trades_df['profit_usd'].sum()
        win_rate = (trades_df['profit_usd'] > 0).mean()
    else:
        total_profit = win_rate = 0

    return trades_df, total_profit, win_rate


