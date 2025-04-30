import MetaTrader5 as mt5
import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt

from intermediate.strats import bollbands, KDJ, backtest, get_signal_combined
from plot import plot_df, create_chart, get_session, init_plot

if not mt5.initialize():
    print("Failed to initialize MT5:", mt5.last_error())
    exit()

symbol = "XAUUSD"
timeframe = mt5.TIMEFRAME_M5
start_pos = 0
count = int(2880)  # 1 days of data at 1-minute intervals

rates = mt5.copy_rates_from_pos(symbol, timeframe, start_pos, count)
mt5.shutdown()

df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
df = bollbands(df, period=20)
df = KDJ(df, period=14, k_smooth=3, d_smooth=10)
df = get_signal_combined(df, thresh=[80, 30])
df = df.iloc[:].copy()
print(df)
df.reset_index(inplace=True)

total_profits = []
win_rates = []
total_trades: list[pd.DataFrame] = []
for hold_period in np.arange(1, 20):
    t0 = time.time()
    trades, total_profit, win_rate = backtest(df, hold_period,3,5)
    total_profits.append(total_profit)
    win_rates.append(win_rate)
    total_trades.append(trades)
    print(f"Hold Period: {hold_period}, Execution Time: {time.time() - t0:.2f} seconds")

print(f"Best Hold Period: {np.argmax(total_profits) + 1}, {np.argmax(win_rates)+1} ")
print(f"Max Total Profit: {total_profits[np.argmax(total_profits)]:.2f} USD, {total_profits[np.argmax(win_rates)]:.2f} USD")
print(f"Max Win Rate: {win_rates[np.argmax(total_profits)]:.2%}, {win_rates[np.argmax(win_rates)]:.2%}")

max_trader = total_trades[np.argmax(total_profits)]
print(max_trader['signal'].value_counts())

confusion_matrix = np.zeros((3, 3), dtype=int)
profit_loss_matrix = np.zeros((3, 3), dtype=float)
# Rows: actual signal [0, 1, -1]
# Columns: [neutral (0), profitable (1), loss (-1)]
print(max_trader)
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

plt.plot(np.arange(1, 20),total_profits, label='Total Profit')
plt.title('Total Profit vs Holding Period')
plt.xlabel('Holding Period (in minutes)')
plt.show()

plt.plot(np.arange(1, 20),win_rates, label='Win Rate')
plt.title('Win Rate vs Holding Period')
plt.xlabel('Holding Period (in minutes)')
plt.show()

plt.plot(range(len(total_trades[np.argmax(total_profits) ]['profit_usd'])),total_trades[np.argmax(total_profits) ]['profit_usd'].cumsum(), label='Cummulative profits')
plt.title('Cummulative profits vs Trades')
plt.xlabel('Trades')
plt.show()

total_trades[np.argmax(total_profits)].to_csv('backtest_trades.csv', index=False)
print(total_trades[np.argmax(total_profits)].describe())

df['sessions'] = df['time'].dt.hour.apply(get_session)
ax1,ax2,ax11 = init_plot(symbol, 100, 'M5')
ax1.set_ylim(df['lower_band'].min() - 10, df['upper_band'].max() + 10)
create_chart(df, ax1, ax2)
ax1, ax2, ax11 = plot_df(df, ax1, ax2, ax11)
ax2.plot(df['index'], 0*np.ones(len(df)), label='lower_thresh', color='green', linestyle='--', linewidth=1)
ax2.plot(df['index'], 100*np.ones(len(df)), label='lower_thresh', color='red', linestyle='--', linewidth=1)
plt.show()