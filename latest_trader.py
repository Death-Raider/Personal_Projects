import MetaTrader5 as mt5
import pandas as pd
from advanced.strats import bollbands, KDJ, backtest, get_signal_combined, get_bias, get_adaptive_sl_tp, calculate_atr
import time
from datetime import datetime
import matplotlib.pyplot as plt

from plot import plot_df, create_chart, get_session, init_plot

def execute_trade(signal, symbol, lot_size=0.01, sl_value=None, tp_value=None, magic=234000):
    tick = mt5.symbol_info_tick(symbol)
    price = tick.ask if signal == 1 else tick.bid
    sl = tp = 0.0
    if sl_value is not None:
        sl = sl_value
    if tp_value is not None:
        tp = tp_value
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

def update_tp_sl(symbol, ticket, sl_val=None, tp_val=None):
    if sl_val is None and tp_val is None:
        print("No SL or TP values provided.")
        return
    
    position = mt5.positions_get(ticket=ticket)
    if not position:
        print("No open position with this ticket.")
        return

    modify_order = {
        "action": mt5.TRADE_ACTION_SLTP,
        "symbol": symbol,
        "sl": sl_val,
        "tp": tp_val,
        "position": ticket,
        "deviation": 10,
        "magic": 234000,
        "comment": "Modify Order",
    }

    result = mt5.order_send(modify_order)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Error modifying order: {result.comment}")
    else:
        print(f"Order modified successfully: SL={sl_val}, TP={tp_val}")
    return result

def get_info(symbol):
    info=mt5.symbol_info(symbol)
    return info

def get_latest_data(symbol, timeframe, count=100):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)  # Get last 100 candles
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def add_values_df(df: pd.DataFrame):
    df = bollbands(df, period=20)
    df = KDJ(df, period=14, k_smooth=3, d_smooth=10)
    df['atr'] = calculate_atr(df, period=14)
    df['atr'] = df['atr'].bfill()  # Fill NaN values in ATR column
    # bias_df = get_latest_data(symbol, timeframe, count=count)
    # bias_df = get_bias(df, period=200)
    df = get_signal_combined(df, thresh=[90, 20], bias=None) # bias_df['bias']
    return df, bias_df

def update_df(symbol:str, timeframe:int, df:pd.DataFrame, count=100):
    latest_df = get_latest_data(symbol, timeframe, count=count)
    if latest_df.empty:
        print("No new data available.")
        return df

    # remove old data from df
    df = df.iloc[:-count] # remove old data from df
    df = pd.concat([df, latest_df], ignore_index=True).drop_duplicates(subset=['time'], keep='last', ignore_index=True)
    return df


DEMO_ACCOUNT_NO = 10820447
DEMO_ACCOUNT_PASS = "eK!K5l#d"
DEMO_SERVER = "VantageInternational-Demo"
REAL_ACCOUNT_NO = 1523662
REAL_ACCOUNT_PASS = "t^g7I4Qy"
REAL_SERVER = "VantageInternational-Live"

if not mt5.initialize(login=DEMO_ACCOUNT_NO, server=DEMO_SERVER, password=DEMO_ACCOUNT_PASS):
    print("Failed to initialize MT5:", mt5.last_error())
    exit()

print(mt5.account_info())

symbol = "XAUUSD"
timeframe = mt5.TIMEFRAME_M5
count = int(2880)
plotting_count = 144
hold_period = 9 # chandels from main.py testing
lot_size = 0.01

sl_multiplier = 1.2
tp_multiplier = 1.5
fake_tp_multiplier = tp_multiplier / 2

entry_state = [None, None, None, None, None, None, None] # (open_trade_ticket, open_trade_time, prev_time, signal, atr, stoploss, takeprofit)

ax1,ax2,ax11 = init_plot(symbol, plotting_count, 'M5')
df = get_latest_data(symbol, timeframe, count=count)
bias_df = df.copy()

try:
    while True:
        # Get latest data
        df = update_df(symbol, timeframe, df, count=2)
        df,bias_df =  add_values_df(df)
        df.reset_index(drop=True, inplace=True)
        # get new signals absed on trend
        plotting_df = df.iloc[-plotting_count:].copy()
        plotting_df.reset_index(inplace=True)
        plotting_df['sessions'] = plotting_df['time'].dt.hour.apply(get_session)
        # current candle time
        latest_candle_time = plotting_df['time'].iloc[-1]

        # Only trade if we have a NEW closed candle
        if (entry_state[2] is None) or (latest_candle_time > entry_state[2]):
            latest_row = plotting_df.iloc[-2]  # <- Use the PREVIOUS fully closed candle
            entry_state[3] = latest_row['signal']  # Update the signal in entry_state

            entry_state[4] = latest_row['atr']  # Update the ATR in entry_state
            print(f"Closed Candle Signal: {entry_state[3]}, Close Price: {latest_row['close']}")

            if entry_state[3] != 0:
                if entry_state[0] is None:
                    entry_state[0] = execute_trade(entry_state[3], symbol, lot_size=lot_size, sl_value=entry_state[5], tp_value=entry_state[6])
                    entry_state[1] = datetime.now()

            entry_state[2] = latest_candle_time  # Update after processing the candle

        if entry_state[0] is not None:
            position = mt5.positions_get(ticket=entry_state[0])
            if not position:
                print("Position closed or not found.")
                entry_state[0] = None  # Reset
                entry_state[1] = None
                entry_state[5] = 0.0
                entry_state[6] = 0.0
                continue
            position = position[0]  # Extract the actual position object
            entry_price = position.price_open
            current_price = position.price_current
            entry_state[5], entry_state[6] = get_adaptive_sl_tp(
                        entry_price=entry_price,
                        current_price=current_price,
                        current_sl= position.sl,
                        current_tp= position.tp,
                        current_fake_tp= None,
                        signal = 1 if position.type == mt5.ORDER_TYPE_BUY else -1,
                        atr_entry= df.iloc[-1]['atr'],  # Use ATR from entry candle
                        sl_multiplier = sl_multiplier,
                        tp_multiplier = tp_multiplier,
                        fake_tp_multiplier=fake_tp_multiplier,
                        aggressive_trail=True,
                        anti_loss_mode=True
                    )
            # print(f"Adaptive SL: {entry_state[5]}, TP: {entry_state[6]}")
            update_tp_sl(symbol, entry_state[0], sl_val=entry_state[5], tp_val=entry_state[6])

        # Check if it's time to close the open position
        if (entry_state[0] is not None and 
            (datetime.now() - entry_state[1]).seconds >= hold_period * timeframe * 60):
            print("closing ticket")
            close_trade(symbol, entry_state[0], lot_size=lot_size)
            entry_state[0] = None  # Reset
            entry_state[1] = None
            entry_state[5] = 0.0
            entry_state[6] = 0.0

        # Plotting
        ax1.set_ylim(plotting_df['lower_band'].min() - 10, plotting_df['upper_band'].max() + 10)
        create_chart(plotting_df, ax1, ax2)
        ax1, ax2, ax11 = plot_df(plotting_df, ax1, ax2, ax11)
        plt.pause(0.01)
        ax1.cla()
        ax2.cla()
        ax11.cla()

except KeyboardInterrupt:
    print("Exiting on user request")
finally:
    mt5.shutdown()
