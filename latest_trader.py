import MetaTrader5 as mt5
import pandas as pd
from intermediate.strats import bollbands, KDJ, backtest, get_signal_combined
import time
from datetime import datetime
import matplotlib.pyplot as plt

from plot import plot_df, create_chart, get_session, init_plot

def get_latest_data(symbol, timeframe, count=100):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)  # Get last 100 candles
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def execute_trade(signal, symbol, lot_size=0.01, sl_dollars=None, tp_dollars=None, magic=234000):
    tick = mt5.symbol_info_tick(symbol)
    price = tick.ask if signal == 1 else tick.bid
    sl = tp = 0.0

    if sl_dollars is not None and tp_dollars is not None:
        if signal == 1:  # Buy
            sl = price - sl_dollars
            tp = price + tp_dollars
        else:  # Sell
            sl = price + sl_dollars
            tp = price - tp_dollars

    order = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_BUY if signal == 1 else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": magic,
        "comment": "Buy Signal" if signal == 1 else "Sell Signal",
        "type_filling": mt5.ORDER_FILLING_IOC,
        "type_time": mt5.ORDER_TIME_GTC,    
    }

    result = mt5.order_send(order)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Error executing trade: {result.comment}")
    else:
        print(f"Trade executed successfully: Ticket {result.order}")
    return result.order

def close_trade(symbol, ticket, lot_size=0.01, magic=234000):
    position = mt5.positions_get(ticket=ticket)
    if not position:
        print("No open position with this ticket.")
        return

    pos = position[0]
    tick = mt5.symbol_info_tick(symbol)
    close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
    price = tick.bid if pos.type == mt5.ORDER_TYPE_BUY else tick.ask

    close_order = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": close_type,
        "price": price,
        "deviation": 10,
        "magic": magic,
        "comment": "Close Order",
        "type_filling": mt5.ORDER_FILLING_IOC,
        "type_time": mt5.ORDER_TIME_GTC,
        "position": ticket,
    }

    result = mt5.order_send(close_order)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Error closing position: {result.comment}")
    else:
        print(f"Position closed successfully at {result.price}")
    return result


def get_info(symbol):
    '''https://www.mql5.com/en/docs/integration/python_metatrader5/mt5symbolinfo_py
    '''
    info=mt5.symbol_info(symbol)
    return info

if not mt5.initialize():
    print("Failed to initialize MT5:", mt5.last_error())
    exit()

print(mt5.account_info())


symbol = "XAUUSD"
timeframe = mt5.TIMEFRAME_M5
count = 144
hold_period = 13 # chandels from main.py testing
lot_size = 0.01
ax1,ax2,ax11 = init_plot(symbol, 100, 'M5')

try:
    open_trade_ticket = None
    open_trade_time = None
    prev_time = None  # <- No need to set datetime.now(), we'll sync to last candle
    while True:
        # Get latest data
        df = get_latest_data(symbol, timeframe, count=count)
        df = bollbands(df, period=20)
        df = KDJ(df, period=14, k_smooth=3, d_smooth=10)
        df.reset_index(inplace=True)
        df = get_signal_combined(df, thresh=[80, 30])

        plotting_df = df.iloc[-100:].copy()
        plotting_df['sessions'] = plotting_df['time'].dt.hour.apply(get_session)

        latest_candle_time = df['time'].iloc[-1]

        # Only trade if we have a NEW closed candle
        if (prev_time is None) or (latest_candle_time > prev_time):
            latest_row = df.iloc[-2]  # <- Use the PREVIOUS fully closed candle
            last_signal = latest_row['signal']
            print(f"Closed Candle Signal: {last_signal}, Close Price: {latest_row['close']}")

            if last_signal != 0:
                if open_trade_ticket is None:
                    open_trade_ticket = execute_trade(last_signal, symbol, lot_size=lot_size, sl_dollars=3, tp_dollars=5)
                    open_trade_time = datetime.now()

            prev_time = latest_candle_time  # Update after processing the candle

        if open_trade_ticket is not None:
            position = mt5.positions_get(ticket=open_trade_ticket)
            if not position:
                print("Position closed or not found.")
                open_trade_ticket = None
                prev_time = None
                open_trade_time = None
                continue

        # Check if it's time to close the open position
        if (open_trade_ticket is not None and 
            (datetime.now() - open_trade_time).seconds >= hold_period * timeframe * 60):
            close_trade(symbol, open_trade_ticket, lot_size=lot_size)
            open_trade_ticket = None  # Reset

        # Plotting
        ax1.set_ylim(plotting_df['lower_band'].min() - 10, plotting_df['upper_band'].max() + 10)
        create_chart(plotting_df, ax1, ax2)
        ax1, ax2, ax11 = plot_df(plotting_df, ax1, ax2, ax11)

        plt.pause(30)
        ax1.cla()
        ax2.cla()
        ax11.cla()
        print("")

except KeyboardInterrupt:
    print("Exiting on user request")
finally:
    mt5.shutdown()
