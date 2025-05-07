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

df = pd.DataFrame(rates)
bias_df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
bias_df['time'] = pd.to_datetime(bias_df['time'], unit='s')
df = bollbands(df, period=20)
df = KDJ(df, period=14, k_smooth=3, d_smooth=10)
df['atr'] = calculate_atr(df, period=14)
bias_df = get_bias(bias_df, period=200)
df = get_signal_combined(df, thresh=[80, 30], bias=bias_df['bias'])
columns = ['bias' ] # 'upper_band', 'lower_band', 'middle_band']
df[columns] = bias_df[columns].copy()
df = df.iloc[-display_count:].copy()

bias_df.reset_index(inplace=True)
df.reset_index( inplace=True)

def get_best_holding_time(df,
                          holding_range_test = [1,20],
                          sl = None, 
                          tp = None,
                          sl_multiplier = 1.5,  # 1.5x ATR for stop-loss
                          tp_multiplier = 3.0,   # 3x ATR for take-profit
                          fake_tp_multiplier = 1.0 # 1x ATR for fake TP
                        ):
    total_profits = []
    win_rates = []
    median_profits = []
    mean_profits = []
    total_trades: list[pd.DataFrame] = []
    holding_range = np.arange(*holding_range_test)
    for hold_period in holding_range:
        t0 = time.time()
        trades, total_profit, win_rate = backtest(df, hold_period, sl, tp)
        median = trades['profit_usd'].median()
        mean = trades['profit_usd'].mean()

        median_profits.append(median)
        mean_profits.append(mean)
        total_profits.append(total_profit)
        win_rates.append(win_rate)
        total_trades.append(trades)
        print(f"Hold Period: {hold_period}, Execution Time: {time.time() - t0:.2f} seconds")

    matrix_analyse = [total_profits, win_rates, median_profits, mean_profits]
    out_matrix = np.zeros((len(matrix_analyse), len(matrix_analyse)), dtype=float)
    for val1 in matrix_analyse:
        for val2 in matrix_analyse:
            out_matrix[matrix_analyse.index(val1), matrix_analyse.index(val2)] = val1[np.argmax(val2)]
    print(out_matrix)

    max_trader = total_trades[np.argmax(total_profits)]
    confusion_matrix = np.zeros((3, 3), dtype=int)
    profit_loss_matrix = np.zeros((3, 3), dtype=float)
    print(max_trader.groupby('tp/sl hit')['profit_usd'].sum())
    print(max_trader['tp/sl hit'].value_counts())

    # Rows: actual signal [0, 1, -1]
    # Columns: [neutral (0), profitable (1), loss (-1)]
    for idx, row in max_trader.iterrows():
        sig = row['signal']
        prof = row['profit_usd']
        
        if sig == 0:
            # No trade
            confusion_matrix[0, 0] += 1
            profit_loss_matrix[0, 0] += 1
        elif sig == 1:
            if prof > 0:
                confusion_matrix[1, 1] += 1  # Good Buy
                profit_loss_matrix[1, 1] += prof  # Good Buy
            else:
                confusion_matrix[1, 2] += 1  # Bad Buy
                profit_loss_matrix[1, 2] += prof  # Bad Buy
        elif sig == -1:
            if prof > 0:
                confusion_matrix[2, 2] += 1  # Good Sell (loss because sell made profit)
                profit_loss_matrix[2, 2] += prof  # Good Sell (loss because sell made profit)
            else:
                confusion_matrix[2, 1] += 1  # Bad Sell (loss because sell made loss)
                profit_loss_matrix[2, 1] += prof  # Bad Sell (loss because sell made loss)

    print("Confusion Matrix (Signal vs Trade Outcome):")
    print(confusion_matrix)
    print("Confusion Matrix (Signal vs Profits):")
    print(profit_loss_matrix)
    print("\nTotal Profits grouped by Signal:")
    print(max_trader.groupby('signal')['profit_usd'].sum())

    # plt.plot(np.arange(*holding_range_test),total_profits, label='Total Profit')
    # plt.title('Total Profit vs Holding Period')
    # plt.xlabel('Holding Period (in minutes)')
    # plt.show()

    # plt.plot(np.arange(*holding_range_test),win_rates, label='Win Rate')
    # plt.title('Win Rate vs Holding Period')
    # plt.xlabel('Holding Period (in minutes)')
    # plt.show()

    plt.plot(range(len(total_trades[np.argmax(total_profits) ]['profit_usd'])),total_trades[np.argmax(total_profits) ]['profit_usd'].cumsum(), label='profits per trade')
    plt.title('profits vs Trades')
    plt.xlabel('Trades')
    plt.show()

    max_trader.to_csv('backtest_trades.csv', index=False)
    print(max_trader.describe())
    return max_trader, holding_range[np.argmax(total_profits)]

best_trader, best_holding_time = get_best_holding_time(df, [1,20], sl=3, tp=5)

print(best_trader)
print(best_holding_time)

# df['sessions'] = df['time'].dt.hour.apply(get_session)
ax1,ax2,ax11 = init_plot(symbol, display_count, 'M5')
ax1.set_ylim(df['lower_band'].min() - 10, df['upper_band'].max() + 10)
create_chart(df, ax1, ax2)
ax1, ax2, ax11 = plot_df(df, ax1, ax2, ax11)
ax2.plot(df['index'], 0*np.ones(len(df)), label='lower_thresh', color='green', linestyle='--', linewidth=1)
ax2.plot(df['index'], 100*np.ones(len(df)), label='lower_thresh', color='red', linestyle='--', linewidth=1)
plt.show()
