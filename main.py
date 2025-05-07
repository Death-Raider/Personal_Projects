import MetaTrader5 as mt5
import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt

from advanced.strats import bollbands, KDJ, backtest, get_signal_combined, get_bias, calculate_atr, get_adaptive_sl_tp
from plot import plot_df, create_chart, get_session, init_plot

if not mt5.initialize():
    print("Failed to initialize MT5:", mt5.last_error())
    exit()

symbol = "XAUUSD"
timeframe = mt5.TIMEFRAME_M5
# bias_timeframe = mt5.TIMEFRAME_H1
start_pos = 0
count = int(2880)  # 1 days of data at 1-minute intervals
display_count = 144

rates = mt5.copy_rates_from_pos(symbol, timeframe, start_pos, count)
mt5.shutdown()
# ========================
# Data Preparation
# ========================

def prepare_data(rates: list, display_count: int) -> pd.DataFrame:
    # Create base DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Calculate indicators
    df = (
        df
        .pipe(bollbands, period=20)
        .pipe(KDJ, period=14, k_smooth=3, d_smooth=10)
        .pipe(lambda x: x.assign(atr=calculate_atr(x, period=14)))
    )
    df['atr'] = df['atr'].bfill()  # Fill NaN values in ATR column
    # Calculate bias and merge
    bias_df = get_bias(df.copy(), period=200)
    df = get_signal_combined(df, bias=bias_df['bias'])
    df = df.merge(bias_df[['time', 'bias']], on='time', how='left')
    return df.iloc[-display_count:].reset_index(drop=True)

# ========================
# Optimization Analysis
# ========================

def optimize_holding_period(
    df: pd.DataFrame,
    hold_range: tuple = (1, 20),
    sl_multiplier: float = 1.5,
    tp_multiplier: float = 3.0,
    fake_tp_multiplier: float = 1.5
) -> tuple:
    holding_periods = range(*hold_range)
    results = []

    for period in holding_periods:
        trades, total_pips, win_rate = backtest(
            df, hold_period=period,
            sl_multiplier=sl_multiplier,
            tp_multiplier=tp_multiplier,
            fake_tp_multiplier=fake_tp_multiplier,
        )
        
        results.append({
            'period': period,
            'total_pips': total_pips,
            'win_rate': win_rate,
            'trades': trades
        })
        print(f"Tested {period} bars | P&L: {total_pips:.1f} pips")

    # Find best period
    best_result = max(results, key=lambda x: x['total_pips'])
    return best_result['trades'], best_result['period'], results

# ========================
# Result Visualization
# ========================

def analyze_results(trades_df: pd.DataFrame) -> None:
    """Generates key performance visualizations"""
    # Equity Curve
    trades_df['equity'] = trades_df['pips'].cumsum()
    trades_df['equity'].plot(title='Equity Curve', grid=True)
    plt.ylabel('Pips')
    plt.show()
    # Exit Reason Analysis
    exit_stats = trades_df.groupby('exit_reason')['pips'].agg(['mean', 'count'])
    exit_stats.plot(kind='bar', subplots=True, title='Performance by Exit Reason')
    plt.show()
    # Holding Period Impact
    trades_df.plot.scatter(x='duration_bars', y='pips', 
                          title='Trade Duration vs Profitability')
    plt.show()

# ========================
# Main Execution
# ========================
if __name__ == "__main__":
    # Prepare data
    processed_df = prepare_data(rates, display_count=display_count)
    
    # Run optimization
    best_trades, best_hold_period, all_results = optimize_holding_period(
        processed_df, hold_range=(1, 20),
        sl_multiplier=1.2,
        tp_multiplier=3,
        fake_tp_multiplier=1.5
    )
    
    # Generate analytics
    analyze_results(best_trades)
    print(best_trades.describe())
    
    # Save results
    best_trades.to_csv('optimal_trades.csv', index=False)
    print(f"Optimal holding period: {best_hold_period} bars")

    # Visualize market context
    processed_df.reset_index(inplace=True)
    print(processed_df)
    ax1,ax2,ax11 = init_plot(symbol, display_count, 'M5')
    ax1.set_ylim(processed_df['lower_band'].min() - 10, processed_df['upper_band'].max() + 10)
    create_chart(processed_df, ax1, ax2)
    ax1, ax2, ax11 = plot_df(processed_df, ax1, ax2, ax11)
    plt.show()