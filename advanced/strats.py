import pandas as pd
from sklearn.linear_model import LinearRegression
from scipy.signal import argrelextrema
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

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df['high']
    low = df['low']
    close = df['close']

    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = true_range.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    return atr

def get_bias(df: pd.DataFrame, period: int, extrema_order: int = 5, thresh_lr: float= 0.1) -> pd.DataFrame:
    assert period > 50, "Period must be greater than 50"
    assert extrema_order > 0, "Extrema order must be greater than 0"
    df = df.copy()
    df = bollbands(df, period=period)
    
    df['middle_band'] = df['middle_band'].rolling(window=50).mean().shift(-80)

    local_max_idx = argrelextrema(df['middle_band'].values, np.greater, order=extrema_order)[0]
    local_min_idx = argrelextrema(df['middle_band'].values, np.less, order=extrema_order)[0]
    pivot_indices = sorted(np.concatenate((local_max_idx, local_min_idx)))
    df['bias'] = 0

    for i in range(len(pivot_indices)-1):
        x = np.arange(int(pivot_indices[i+1] - pivot_indices[i])).reshape(-1, 1)
        y = df['middle_band'].iloc[pivot_indices[i]:pivot_indices[i+1]].values.reshape(-1, 1)

        model = LinearRegression().fit(x, y)
        slope = model.coef_[0][0]
        df['slope'] = slope
        if slope >= thresh_lr:
            df.loc[pivot_indices[i]:, 'bias'] = 1
        elif slope <= -thresh_lr:
            df.loc[pivot_indices[i]:, 'bias'] = -1
    return df

def bollbands(df: pd.DataFrame, period: int):
    df['middle_band'] = df['close'].rolling(window=period).mean()
    df['std_dev'] = df['close'].rolling(window=period).std()
    df['upper_band'] = df['middle_band'] + (2 * df['std_dev'])
    df['lower_band'] = df['middle_band'] - (2 * df['std_dev'])
    df.bfill(inplace=True)
    return df

def get_signal_combined(df: pd.DataFrame, thresh: list[int] = [80, 20], bias: pd.DataFrame = None) -> pd.DataFrame:
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
    if bias is None:
        df.loc[(bb_buy | (kdj_buy_cross | j_cross_up)), 'signal'] = 1    # Strong Buy
        df.loc[(bb_sell | ( kdj_sell_cross | j_cross_down)), 'signal'] = -1  # Strong Sell
    else:
        # when bias == 1, works. otherwise no rows are effected
        df.loc[(bb_buy | (kdj_buy_cross | j_cross_up)) & (bias == 1), 'signal'] = 1    # Strong Buy
        df.loc[(bb_sell & ( kdj_sell_cross | j_cross_down)) & (bias == 1), 'signal'] = -1  # Strong Sell
        # when bias == -1, works. otherwise no rows are effected
        df.loc[(bb_buy & (kdj_buy_cross | j_cross_up)) & (bias == -1), 'signal'] = 1    # Strong Buy
        df.loc[(bb_sell | ( kdj_sell_cross | j_cross_down)) & (bias == -1), 'signal'] = -1  # Strong Sell

    return df


def backtest(df: pd.DataFrame, hold_period: int, sl_dollars: float = None, tp_dollars: float = None):
    trades = []
    idx = 1  # Start at 1 to allow look-back
    in_trade = False
    tp_hits = 0
    timeout_hits = 0
    max_drawup = max_drawdown = 0    
    while idx < len(df) - 1:
        # sl, tp = get_adaptive_sl_tp()
        if not in_trade:
            signal = df.loc[idx - 1, 'signal']  # <- use signal from PREVIOUS candle (like live)
            if signal == 0:
                idx += 1
                continue

            entry_price = df.loc[idx, 'open']  # Enter trade at next candle open
            entry_time = df.loc[idx, 'time']

            trade_start_idx = idx
            in_trade = True
            idx += 1
            # Setup SL/TP
            sl_price = tp_price = None
            if sl_dollars is not None and tp_dollars is not None:
                if signal == 1:
                    sl_price = entry_price - sl_dollars
                    tp_price = entry_price + tp_dollars
                else:
                    sl_price = entry_price + sl_dollars
                    tp_price = entry_price - tp_dollars
            continue

        # Check exit by hold period
        exit_idx = trade_start_idx + hold_period
        max_drawup = df.loc[trade_start_idx:idx, 'high'].max() - entry_price
        max_drawdown = entry_price - df.loc[trade_start_idx:idx, 'low'].min()
        
        if idx >= exit_idx or idx >= len(df):
            exit_price = df.loc[min(idx, len(df)-1), 'close']
            exit_time = df.loc[min(idx, len(df)-1), 'time']
            profit = (exit_price - entry_price) if signal == 1 else (entry_price - exit_price)
            tpsl_hit = 0
            if tp_price is not None and sl_price is not None:
                if profit > tp_dollars:
                    profit = tp_dollars
                    tp_hits += 1
                    tpsl_hit = 2
                if profit < -sl_dollars:
                    profit = -sl_dollars
                    tp_hits += 1
                    tpsl_hit = 1

            trades.append({
                'entry_time': entry_time,
                'exit_time': exit_time,
                'signal': signal,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'profit_usd': profit,
                'tp/sl hit': tpsl_hit,
                'drawup': max_drawup,
                'drawdown': max_drawdown
            })

            in_trade = False
            idx = exit_idx  # move ahead
            timeout_hits += 1
            continue

        # SL/TP logic using high/low
        high = df.loc[idx, 'high']
        low = df.loc[idx, 'low']

        hit_sl = hit_tp = False
        if signal == 1:
            hit_tp = tp_price is not None and high >= tp_price
            hit_sl = sl_price is not None and low <= sl_price
        else:
            hit_tp = tp_price is not None and low <= tp_price
            hit_sl = sl_price is not None and high >= sl_price

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
                'tp/sl hit': 1 if hit_sl else 2,
                'drawup': max_drawup,
                'drawdown': max_drawdown
            })

            in_trade = False
            idx += 1
            tp_hits += 1
            continue

        idx += 1
    print("Take Profit/ Stop Loss hits:", tp_hits)
    print("Timeout hits", timeout_hits)
    trades_df = pd.DataFrame(trades)
    if not trades_df.empty:
        total_profit = trades_df['profit_usd'].sum()
        win_rate = (trades_df['profit_usd'] > 0).mean()
    else:
        total_profit = win_rate = 0

    return trades_df, total_profit, win_rate

def get_adaptive_sl_tp(
    entry_price: float,
    current_price: float,
    signal: int,
    max_tp_dollars: float,
    min_sl_dollars: float,
    fake_tp_dollars: float = 3.0,
    aggressive_trail: bool = True,
    anti_loss_mode: bool = True
) -> tuple:
    # BUY TRADE
    if signal == 1:
        tp = entry_price + max_tp_dollars
        sl = entry_price - min_sl_dollars
        fake_tp = entry_price + fake_tp_dollars
        unrealized_profit = current_price - entry_price

        # If price is moving in our favor and crossed fake TP
        if current_price >= fake_tp:
            # SL gets pulled up to break even first
            sl = entry_price
            # Then trail with price gain beyond fake TP
            if aggressive_trail:
                sl += current_price - fake_tp  # lock partial gains

        # If price is against us, shrink both TP and SL
        elif current_price < entry_price and anti_loss_mode:
            sl = entry_price - (min_sl_dollars * 0.5)  # tighter stop
            tp = entry_price + (max_tp_dollars * 0.4)  # take what we can

    # SELL TRADE
    elif signal == -1:
        tp = entry_price - max_tp_dollars
        sl = entry_price + min_sl_dollars
        fake_tp = entry_price - fake_tp_dollars
        unrealized_profit = entry_price - current_price

        if current_price <= fake_tp:
            sl = entry_price
            if aggressive_trail:
                sl -= fake_tp - current_price

        elif current_price > entry_price and anti_loss_mode:
            sl = entry_price + (min_sl_dollars * 0.5)
            tp = entry_price - (max_tp_dollars * 0.4)

    else:
        raise ValueError("Signal must be 1 (buy) or -1 (sell)")

    return round(sl, 2), round(tp, 2)


