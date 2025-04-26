# 📚 MetaTrader5 Python API - Full Documentation

## Introduction

The **MetaTrader5** (MT5) Python package allows Python programs to interact with the MetaTrader 5 trading platform.  
It provides methods to access market data, trading account information, execute trades, and manage orders.

---

# API Reference

## 🔌 Connection Functions

### `initialize(path=None, login=None, password=None, server=None, portable=False)`
- **Description:** Initializes a connection to a MetaTrader 5 terminal.
- **Parameters:**
  - `path` (str, optional): Full path to the terminal executable (`terminal64.exe`).
  - `login` (int, optional): Trading account number.
  - `password` (str, optional): Trading account password.
  - `server` (str, optional): Broker server name.
  - `portable` (bool, optional): If `True`, runs the terminal in portable mode.
- **Returns:** `True` if successful, `False` otherwise.

---

### `shutdown()`
- **Description:** Closes the connection with the MetaTrader 5 terminal.
- **Returns:** `None`

---

## 📈 Market Data Functions

### `copy_rates_from(symbol, timeframe, date_from, count)`
- **Description:** Retrieves historical price rates starting from a specific date.
- **Parameters:**
  - `symbol` (str): Trading symbol (e.g., `"EURUSD"`).
  - `timeframe` (enum): Timeframe (e.g., `TIMEFRAME_M1`, `TIMEFRAME_H1`, etc.).
  - `date_from` (datetime): Starting date and time.
  - `count` (int): Number of bars (candlesticks) to retrieve.
- **Returns:** NumPy structured array with fields: `time`, `open`, `high`, `low`, `close`, `tick_volume`, `spread`, `real_volume`.

---

### `copy_rates_from_pos(symbol, timeframe, start_pos, count)`
- **Description:** Retrieves historical price rates starting from a specified bar index.
- **Parameters:**
  - `symbol` (str)
  - `timeframe` (enum)
  - `start_pos` (int): Starting bar index (0 = latest bar).
  - `count` (int)
- **Returns:** NumPy structured array.

---

### `copy_rates_range(symbol, timeframe, date_from, date_to)`
- **Description:** Retrieves historical rates between two dates.
- **Parameters:**
  - `symbol` (str)
  - `timeframe` (enum)
  - `date_from` (datetime)
  - `date_to` (datetime)
- **Returns:** NumPy structured array.

---

### `copy_ticks_from(symbol, time_from, count, flags)`
- **Description:** Retrieves ticks starting from a specific date/time.
- **Parameters:**
  - `symbol` (str)
  - `time_from` (datetime)
  - `count` (int)
  - `flags` (int): Tick type (all, bid, ask, etc.).
- **Returns:** NumPy array of tick data.

---

### `copy_ticks_range(symbol, time_from, time_to, flags)`
- **Description:** Retrieves ticks between two times.
- **Returns:** NumPy array.

---

## 🔍 Symbol Functions

### `symbols_get(group="")`
- **Description:** Retrieves all available symbols, or symbols matching a group.
- **Parameters:**
  - `group` (str, optional): Filter symbols (wildcards allowed, like `"EUR*"`).
- **Returns:** List of symbol structures (named tuples).

---

### `symbol_info(symbol)`
- **Description:** Retrieves full information about a symbol.
- **Parameters:**
  - `symbol` (str)
- **Returns:** Symbol information named tuple (e.g., `symbol_info.name`, `symbol_info.trade_mode`, etc.)

---

### `symbol_select(symbol, select)`
- **Description:** Adds or removes a symbol from the Market Watch.
- **Parameters:**
  - `symbol` (str)
  - `select` (bool): `True` to add, `False` to remove.
- **Returns:** `True` if successful.

---

## 📑 Order and Trade Functions

### `order_send(request)`
- **Description:** Sends a new trading order.
- **Parameters:**
  - `request` (dict): Order parameters.
- **Returns:** Result structure with execution info.

---

### `order_check(request)`
- **Description:** Checks the validity of an order without sending it.
- **Parameters:**
  - `request` (dict)
- **Returns:** Check result structure.

---

### `positions_get(symbol=None)`
- **Description:** Retrieves open positions.
- **Parameters:**
  - `symbol` (str, optional): If set, returns only positions for the given symbol.
- **Returns:** List of position structures.

---

### `orders_get(symbol=None)`
- **Description:** Retrieves pending orders.
- **Parameters:**
  - `symbol` (str, optional)
- **Returns:** List of order structures.

---

### `deals_get(symbol=None, from_date=None, to_date=None)`
- **Description:** Retrieves past deals (executed orders).
- **Parameters:**
  - `symbol` (str, optional)
  - `from_date` (datetime, optional)
  - `to_date` (datetime, optional)
- **Returns:** List of deal structures.

---

## 💵 Account Functions

### `account_info()`
- **Description:** Retrieves full information about the current trading account.
- **Returns:** Account information named tuple (fields like `balance`, `equity`, `login`, `leverage`, etc.).

---

# 🛠️ Constants (Timeframes)

| Name | Value | Description |
|:-----|:------|:------------|
| `TIMEFRAME_M1` | 1 | 1-minute candles |
| `TIMEFRAME_M5` | 5 | 5-minute candles |
| `TIMEFRAME_M15` | 15 | 15-minute candles |
| `TIMEFRAME_H1` | 60 | 1-hour candles |
| `TIMEFRAME_D1` | 1440 | 1-day candles |
| *(and many others like H4, W1, MN1)* | | |

---

# 🛟 Error Handling

- Always check the return value of `initialize()` and `order_send()`.
- Use `mt5.last_error()` to get error descriptions if a function fails.

---

# 📋 Example

```python
import MetaTrader5 as mt5

# Connect
if not mt5.initialize():
    print("Failed to connect:", mt5.last_error())
    exit()

# Get account info
account = mt5.account_info()
print("Balance:", account.balance)

# Get EURUSD 1-hour data
rates = mt5.copy_rates_from("EURUSD", mt5.TIMEFRAME_H1, datetime.datetime.now() - datetime.timedelta(days=1), 50)

# Close
mt5.shutdown()
```

---

# ✅ Done!
