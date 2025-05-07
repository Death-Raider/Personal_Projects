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
    
    df['middle_band'] = df['middle_band'].rolling(window=50).mean()
    df['middle_band'] = df['middle_band'].bfill()  # Fill NaN values in middle_band column

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


def backtest(
    df: pd.DataFrame, 
    hold_period: int, 
    sl_multiplier: float = 1.5,  # Changed to multipliers
    tp_multiplier: float = 3.0,
    fake_tp_multiplier: float = 1.0
):
    trades = []
    idx = 1  # Start at 1 to allow look-back
    tp_hits = 0
    timeout_hits = 0
    in_trade = False
    while idx < len(df) - 1:
        if 'signal' not in df.columns:
            raise ValueError("DataFrame must contain 'signal' column")
            
        # Entry logic ---------------------------------------------------------
        if not in_trade:
            signal = df.loc[idx - 1, 'signal']  # Signal from previous candle
            if signal == 0:
                idx += 1
                continue

            entry_price = df.loc[idx, 'open']
            entry_time = df.loc[idx, 'time']
            entry_idx = idx
            
            # Initialize trade state
            current_sl = None
            current_tp = None
            prev_sl_doller = None
            prev_tp_doller = None
            max_price = entry_price  # For drawup/drawdown tracking
            min_price = entry_price
            in_trade = True
            idx += 1
            continue

        # Trade monitoring ----------------------------------------------------
        current_price = df.loc[idx, 'open']
        high = df.loc[idx, 'high']
        low = df.loc[idx, 'low']
        
        # Update max/min prices for drawup/drawdown
        max_price = max(max_price, high)
        min_price = min(min_price, low)
        current_drawup = max_price - entry_price if signal == 1 else entry_price - min_price
        current_drawdown = entry_price - min_price if signal == 1 else max_price - entry_price

        # Adaptive SL/TP updates
        if current_sl is not None and current_tp is not None:
            prev_sl_doller = entry_price - current_sl if signal == 1 else current_sl - entry_price
            prev_tp_doller = current_tp - entry_price if signal == 1 else entry_price - current_tp

        current_sl, current_tp = get_adaptive_sl_tp(
            entry_price=entry_price,
            current_price=current_price,
            signal=signal,
            atr_entry=df.loc[entry_idx, 'atr'],  # Use ATR from entry candle
            sl_multiplier=sl_multiplier,
            tp_multiplier=tp_multiplier,
            fake_tp_multiplier=fake_tp_multiplier,
            aggressive_trail=True,
            anti_loss_mode=True
        )

        new_sl_doller = entry_price - current_sl if signal == 1 else current_sl - entry_price
        new_tp_doller = current_tp - entry_price if signal == 1 else entry_price - current_tp

        print("updated:",(prev_sl_doller, prev_tp_doller) , (new_sl_doller,new_tp_doller), "PnL:",entry_price - current_price if signal == -1 else current_price - entry_price)
        # Exit checks ---------------------------------------------------------
        exit_reason = None
        exit_price = None
        
        # 1. SL/TP hit
        if signal == 1:
            if low <= current_sl:
                exit_price = current_sl
                exit_reason = 'SL'
            elif high >= current_tp:
                exit_price = current_tp
                exit_reason = 'TP'
        else:
            if high >= current_sl:
                exit_price = current_sl
                exit_reason = 'SL'
            elif low <= current_tp:
                exit_price = current_tp
                exit_reason = 'TP'

        # 2. Hold period expiration
        if not exit_reason and (idx - entry_idx >= hold_period):
            exit_price = df.loc[idx, 'close']
            exit_reason = 'Timeout'

        # Record trade if exit triggered
        if exit_reason:
            profit = (exit_price - entry_price)*100 if signal == 1 else (entry_price - exit_price)*100  # Assuming XAUUSD ($0.01/pip)
            
            trades.append({
                'entry_time': entry_time,
                'exit_time': df.loc[idx, 'time'],
                'direction': 'Long' if signal == 1 else 'Short',
                'entry_price': entry_price,
                'exit_price': exit_price,
                'pips': profit,
                'exit_reason': exit_reason,
                'max_drawup_pips': current_drawup*100,
                'max_drawdown_pips': current_drawdown*100,
                'duration_bars': idx - entry_idx,
                'take_profit': current_tp - entry_price if signal == 1 else entry_price - current_tp,
                'stop_loss': entry_price - current_sl if signal == 1 else current_sl - entry_price,
            })

            if exit_reason in ['TP', 'SL']: 
                tp_hits += 1
            else:
                timeout_hits += 1

            in_trade = False
            idx += 1  # Move to next candle after exit
            continue

        idx += 1

    # Results calculation
    trades_df = pd.DataFrame(trades)
    if not trades_df.empty:
        trades_df['win'] = trades_df['pips'] > 0
        total_pips = trades_df['pips'].sum()
        win_rate = trades_df['win'].mean()
    else:
        total_pips = win_rate = 0

    print(f"TP/SL hits: {tp_hits} | Timeouts: {timeout_hits}")
    print(f"Total P&L: {total_pips:.1f} pips | Win Rate: {win_rate:.1%}")
    
    return trades_df, total_pips, win_rate

def get_adaptive_sl_tp(
    entry_price: float,
    current_price: float,
    signal: int,
    atr_entry: float,
    tp_multiplier: float,
    sl_multiplier: float,
    fake_tp_multiplier: float = 3.0,
    aggressive_trail: bool = True,
    anti_loss_mode: bool = True
) -> tuple:
    max_tp_dollars = tp_multiplier * atr_entry
    min_sl_dollars = sl_multiplier * atr_entry
    fake_tp_dollars = fake_tp_multiplier * atr_entry
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


