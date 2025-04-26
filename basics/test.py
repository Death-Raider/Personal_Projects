import MetaTrader5 as mt5
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from strats import bollbands, check_patterns

if not mt5.initialize():
    print("Failed to initialize MT5:", mt5.last_error())
    exit()

symbol = "XAUUSD"
timeframe = mt5.TIMEFRAME_M5
start_pos = 1
count = 1000

rates = mt5.copy_rates_from_pos(symbol, timeframe, start_pos, count)
mt5.shutdown()

df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
df = bollbands(df, period=20)
df.reset_index(inplace=True)
df = check_patterns(df)

fig, ax = plt.subplots(figsize=(14, 7))
width = 0.6

for idx, row in df.iterrows():
    x = row['index']

    ax.plot([x, x], [row['low'], row['high']], color='black', linewidth=1)

    if row['close'] >= row['open']:
        color = 'green'
        lower = row['open']
        height = row['close'] - row['open']
    else:
        color = 'red'
        lower = row['close']
        height = row['open'] - row['close']

    rect = Rectangle(
        (x - width/2, lower),
        width,
        height,
        color=color,
        edgecolor='black'
    )
    ax.add_patch(rect)

valid = df.dropna()
ax.plot(valid['index'], valid['middle_band'], label='Middle Band (SMA)', color='blue', linewidth=1.5)
ax.plot(valid['index'], valid['upper_band'], label='Upper Band', color='purple', linestyle='--', linewidth=1)
ax.plot(valid['index'], valid['lower_band'], label='Lower Band', color='purple', linestyle='--', linewidth=1)
ax2 = ax.twinx()
ax2.plot(df['index'], df['signal'], label='signal', color='green', linestyle='-', linewidth=1)
# ax2.plot(df['index'], df['bearish'], label='bullish', color='red', linestyle='-', linewidth=1)

ax.set_xticks(df['index'][::5])
ax.set_xticklabels(df['time'].dt.strftime('%Y-%m-%d %H:%M')[::5], rotation=45)

ax.set_title(f"{symbol} - Last {count} H1 Candles", fontsize=16)
ax.set_xlabel("Time")
ax.set_ylabel("Price")
plt.grid(True)
plt.tight_layout()

plt.show()
