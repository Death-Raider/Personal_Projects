# statistical_modeling/Risk_Modeling.py
- Given the OHLCV data, compute 268 features

# statistical_modeling/risk_dashboard.py
- Creates a dashboard (large image) of multiple plots based on the computed features from Risk_Modeling.  

# cfd-pde.py
- Numeric solution for custom Stochastic Partial Differential Equation 

# config_loader.py
- Loads config.json for other files

# csv_manager.py (isolated from workflow)
- Automatically maintains historical price values in CSV file which gets incrementally updated for new bars

# data_fetcher.py
- Handles MT5 connection establishment and data pulling

# logger.py (isolated from workflow)
- Handles logging of trade updates as well as system updates 

# ols.py
- Computes OLS on market data on a rolling window and trains a MLP to predict the slope given previous candle

# pde_backtest.py
- Uses the cfd-pde to compute probabilities for entry and recomputs based on market shifts. Takes positions based on signals by signal_gen

# PDE_parameters.py
- Class for handling all parameters required for cfd-pde

# plotting.py
- Handles plotting of results of backtesting along with generating summaries based on results

# position_manager.py (isolated from workflow)
- Dynamically handles position state and adjusts TP and SL dynamically based on certain config values

# signal_gen.py
- Uses the active cfd-pde distribution and other features to provide a trade position

# strats.py
- Integration of all files such that 
  - data is loaded
  - features are extracted
  - model is trained and saved
  - PDE based backtesting on the loaded data is conducted
  - backtesting statistics are saved appropriately 