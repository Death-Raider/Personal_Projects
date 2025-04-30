import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from matplotlib import colors

asia_start = 21  # 11:00 PM UTC
asia_end = 8     # 8:00 AM UTC

europe_start = 7  # 7:00 AM UTC
europe_end = 16   # 4:00 PM UTC

na_start = 12     # 12:00 PM UTC
na_end = 21       # 9:00 PM UTC

def get_session(hour):
    sessions = []
    if asia_start <= hour or hour < asia_end:
        sessions.append('Asia')
    if europe_start <= hour < europe_end:
        sessions.append('Europe')
    if na_start <= hour < na_end:
        sessions.append('North America')
    return sessions

def blend_colors(color1, color2):
    c1 = np.array(colors.to_rgba(color1)[:3])
    c2 = np.array(colors.to_rgba(color2)[:3])
    blended = (c1 + c2) / 2
    return tuple(blended)

session_colors = {
    'Asia': 'lightblue',
    'Europe': 'lightgreen',
    'North America': 'lightcoral'
}

def highlight_sessions(ax1, row, width):
    if len(row['sessions']) > 1:  # Multiple sessions overlapping
        blended_color = blend_colors(session_colors[row['sessions'][0]], session_colors[row['sessions'][1]])
        ax1.add_patch(Rectangle(
            (row['index'] - width / 2, ax1.get_ylim()[0]),
            width,
            ax1.get_ylim()[1] - ax1.get_ylim()[0],  # Full height of the axis
            color=blended_color,
            alpha=0.2  # Make the box translucent
        ))
    else:  # Only one session, use its color
        session_color = session_colors.get(row['sessions'][0], 'gray')  # Default to gray if no session
        ax1.add_patch(Rectangle(
            (row['index'] - width / 2, ax1.get_ylim()[0]),
            width,
            ax1.get_ylim()[1] - ax1.get_ylim()[0],  # Full height of the axis
            color=session_color,
            alpha=0.2  # Make the box translucent
        ))
def init_plot(symbol, count, timeframe):
    fig = plt.figure(figsize=(10, 8))
    gs = fig.add_gridspec(nrows=4, ncols=1)
    ax1 = fig.add_subplot(gs[0:3, 0])
    ax2 = fig.add_subplot(gs[3, 0], sharex=ax1)
    ax11 = ax1.twinx()
    ax1.set_title(f"{symbol} - Last {count} {timeframe} Candles", fontsize=16)
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Price")
    return ax1, ax2, ax11

def create_chart(df, ax1, ax2)->None:
    width = 0.6
    for idx, row in df.iterrows():
        x = row['index']
        ax1.plot([x, x], [row['low'], row['high']], color='black', linewidth=1)

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
        )
        ax1.add_patch(rect)
        highlight_sessions(ax1, row, width)  # Highlight sessions

def plot_df(df, ax1, ax2, ax11)->None:
    valid = df.dropna()
    ax1.plot(valid['index'], valid['middle_band'], label='Middle Band (SMA)', color='blue', linewidth=1.5)
    ax1.plot(valid['index'], valid['upper_band'], label='Upper Band', color='purple', linestyle='--', linewidth=1)
    ax1.plot(valid['index'], valid['lower_band'], label='Lower Band', color='purple', linestyle='--', linewidth=1)
    ax11.plot(valid['index'], valid['signal'], label='Signal', color='orange', linestyle='--', linewidth=1)

    ax2.plot(df['index'], df['kdj_k'], label='k', color='yellow', linestyle='-', linewidth=1)
    ax2.plot(df['index'], df['kdj_d'], label='d', color='orange', linestyle='-', linewidth=1)
    ax2.plot(df['index'], df['kdj_j'], label='j', color='skyblue', linestyle='-', linewidth=1)
    # ax[0].set_xticklabels(df['time'].dt.strftime('%Y-%m-%d %H:%M')[::5], rotation=45)
    plt.setp(ax1.get_xticklabels(), visible=False)

    plt.grid(True)
    plt.tight_layout()
    return ax1, ax2, ax11,
