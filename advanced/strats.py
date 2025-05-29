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
    assert extrema_order > 0, "Extrema order must be greater than 0"
    df = df.copy()
    df = bollbands(df, period=period)
    
    df['middle_band'] = df['middle_band'].rolling(window=50).mean()
    df['middle_band'] = df['middle_band'].bfill()  # Fill NaN values in middle_band column

    local_max_idx = argrelextrema(df['middle_band'].values, np.greater, order=extrema_order)[0]
    local_min_idx = argrelextrema(df['middle_band'].values, np.less, order=extrema_order)[0]
    pivot_indices = sorted(np.concatenate((local_max_idx, local_min_idx)))
    pivot_indices.append(len(df)-1)  # Append the end of the DataFrame
    pivot_indices.insert(0, 0)  # Ensure we start from the first index
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

def get_signal_combined(df: pd.DataFrame, thresh: list[int] = [80, 20], bias: pd.Series = None) -> pd.DataFrame:
    df = df.copy()
    df['signal'] = 0

    # ---- Bollinger Band Extremes ----
    bb_buy = df['close'] < (df['lower_band'] - 5)
    bb_sell = df['close'] > (df['upper_band'] + 5)

    # ---- KDJ Crosses ----
    kdj_buy_cross = (df['kdj_k'].shift(1) < df['kdj_d'].shift(1)) & (df['kdj_k'] > df['kdj_d'])
    kdj_sell_cross = (df['kdj_k'].shift(1) > df['kdj_d'].shift(1)) & (df['kdj_k'] < df['kdj_d'])

    # ---- J Threshold Crosses ----
    j_cross_up = (df['kdj_j'].shift(1) < thresh[1]) & (df['kdj_j'] > thresh[1])
    j_cross_down = (df['kdj_j'].shift(1) > thresh[0]) & (df['kdj_j'] < thresh[0])

    # ---- Divergences ----
    # Bullish divergence: price makes lower low, J makes higher low
    bull_div = (df['low'].shift(1) > df['low']) & (df['kdj_j'].shift(1) < df['kdj_j'])
    # Bearish divergence: price makes higher high, J makes lower high
    bear_div = (df['high'].shift(1) < df['high']) & (df['kdj_j'].shift(1) > df['kdj_j'])

    # ---- Pullback Entries ----
    pullback_buy = (
        (df['kdj_j'] < 20) &
        (df['kdj_j'].shift(1) < df['kdj_j']) &
        (df['close'] > df['middle_band'])
    )
    pullback_sell = (
        (df['kdj_j'] > 80) &
        (df['kdj_j'].shift(1) > df['kdj_j']) &
        (df['close'] < df['middle_band'])
    )

    # ---- Breakout Entries ----
    breakout_buy = (kdj_buy_cross | j_cross_up) & (df['close'] > df['upper_band'])
    breakout_sell = (kdj_sell_cross | j_cross_down) & (df['close'] < df['lower_band'])

    # ---- Final Signal Assignment ----
    if bias is None:
        # No trend bias — raw signals
        df.loc[bb_buy | kdj_buy_cross | j_cross_up | pullback_buy | breakout_buy | bull_div, 'signal'] = 1
        df.loc[bb_sell | kdj_sell_cross | j_cross_down | pullback_sell | breakout_sell | bear_div, 'signal'] = -1
    else:
        # Bullish bias → allow only long entries
        long_mask = bias == 1
        df.loc[bb_buy & long_mask, 'signal'] = 1
        df.loc[kdj_buy_cross & long_mask, 'signal'] = 1
        df.loc[j_cross_up & long_mask, 'signal'] = 1
        df.loc[pullback_buy & long_mask, 'signal'] = 1
        df.loc[breakout_buy & long_mask, 'signal'] = 1
        df.loc[bull_div & long_mask, 'signal'] = 1

        # Bearish bias → allow only short entries
        short_mask = bias == -1
        df.loc[bb_sell & short_mask, 'signal'] = -1
        df.loc[kdj_sell_cross & short_mask, 'signal'] = -1
        df.loc[j_cross_down & short_mask, 'signal'] = -1
        df.loc[pullback_sell & short_mask, 'signal'] = -1
        df.loc[breakout_sell & short_mask, 'signal'] = -1
        df.loc[bear_div & short_mask, 'signal'] = -1

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
            current_tp=current_tp,
            current_sl=current_sl,
            current_fake_tp=None,
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

        # print("updated:",(prev_sl_doller, prev_tp_doller) , (new_sl_doller,new_tp_doller), "PnL:",entry_price - current_price if signal == -1 else current_price - entry_price)
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
            profit = (exit_price - entry_price) if signal == 1 else (entry_price - exit_price)  # Assuming XAUUSD ($0.01/pip)
            
            trades.append({
                'entry_time': entry_time,
                'exit_time': df.loc[idx, 'time'],
                'direction': 'Long' if signal == 1 else 'Short',
                'entry_price': entry_price,
                'exit_price': exit_price,
                'pips': profit,
                'exit_reason': exit_reason,
                'max_drawup_pips': current_drawup,
                'max_drawdown_pips': current_drawdown,
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
    current_sl: float,
    current_tp: float,
    current_fake_tp: float,
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
    sl = current_sl
    tp = current_tp
    # BUY TRADE
    if signal == 1:
        calc_tp = round(entry_price + max_tp_dollars,2)
        calc_sl = round(entry_price - min_sl_dollars,2)
        calc_fake_tp = round(entry_price + fake_tp_dollars,2)

        if current_tp is None:
            current_tp = calc_tp
        if current_sl is None:
            current_sl = calc_sl
        
        if current_price >= entry_price:
            # market is in our favour
            # check if fake_tp is hit
            if current_price >= calc_fake_tp:
                # fake tp is hit, update the stop loss and take profit but making sure it doesnt go below the current stop loss
                # and take profit
                sl = max(current_sl, entry_price) # stop loss is shifted to the entry price
                tp = max(calc_tp, current_tp) # take profit is shifted to the calculated take profit
                if aggressive_trail:
                    # if aggressive trail is enabled, we can shift the stop loss to the change in price above the fake tp
                    # but not below the current stop loss
                    sl = max(sl, entry_price + (current_price - calc_fake_tp))
            else: # price is below fake tp
                if anti_loss_mode:
                    # if anti loss mode is enabled, we can shift the stop loss to the entry price
                    sl = max(current_sl, calc_sl + (min_sl_dollars * 0.4)) # reduce the stop loss
                    tp = round(entry_price + max_tp_dollars*0.7, 2) # reduce the profits a bit
        else:
            # market is against us
            # check for anti loss mode and check with calc and current values
            if anti_loss_mode:
                # if anti loss mode is enabled, we can shift the stop loss to the entry price
                sl = round(entry_price - min_sl_dollars*0.6, 2)
                tp = round(entry_price + max_tp_dollars*0.6, 2)
    elif signal == -1:
            calc_tp = round(entry_price - max_tp_dollars,2)
            calc_sl = round(entry_price + min_sl_dollars,2)
            calc_fake_tp = round(entry_price - fake_tp_dollars,2)

            if current_tp is None:
                current_tp = calc_tp
            if current_sl is None:
                current_sl = calc_sl
            
            if current_price <= entry_price:
                # market is in our favour
                # check if fake_tp is hit
                if current_price <= calc_fake_tp:
                    # fake tp is hit, update the stop loss and take profit but making sure it doesnt go below the current stop loss
                    # and take profit
                    sl = min(current_sl, entry_price) # stop loss is shifted to the entry price
                    tp = min(calc_tp, current_tp) # take profit is shifted to the calculated take profit
                    if aggressive_trail:
                        # if aggressive trail is enabled, we can shift the stop loss to the change in price above the fake tp
                        # but not below the current stop loss
                        sl = min(sl, entry_price - ( -current_price + calc_fake_tp))
                else: # price is below fake tp
                    if anti_loss_mode:
                        # if anti loss mode is enabled, we can shift the stop loss to the entry price
                        sl = min(current_sl, calc_sl - (min_sl_dollars * 0.5)) # reduce the stop loss
                        tp = round(entry_price - max_tp_dollars*0.7, 2) # reduce the profits a bit
            else:
                # market is against us
                # check for anti loss mode and check with calc and current values
                if anti_loss_mode:
                    # if anti loss mode is enabled, we can shift the stop loss to the entry price
                    sl = round(entry_price + min_sl_dollars*0.4, 2)
                    tp = round(entry_price - max_tp_dollars*0.4, 2)

    return round(sl, 2), round(tp, 2)


