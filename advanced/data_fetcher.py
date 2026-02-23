import MetaTrader5 as mt5
import pandas as pd
from config_loader import config
from logger import logger

class DataFetcher:
    def __init__(self):
        self.connected = False
        self.dataframes = {}
        self.last_bar_times = {}
    
    def connect(self):
        account = config.get('mt5', 'account')
        password = config.get('mt5', 'password')
        server = config.get('mt5', 'server')
        
        if not mt5.initialize(login=account, server=server, password=password):
            error = mt5.last_error()
            logger.log_error(f"MT5 initialization failed: {error}")
            return False
        
        self.connected = True
        logger.log_system_event('mt5_connect', f"Connected to {server}")
        return True
    
    def disconnect(self):
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.log_system_event('mt5_disconnect', "Disconnected from MT5")
    
    def fetch_data(self, timeframe_name):
        if not self.connected:
            return None
        
        symbol = config.get('trading', 'symbol')
        timeframe_code = config.get('trading', 'timeframes', timeframe_name)
        bars_count = config.get('trading', 'data_bars', timeframe_name)
        
        rates = mt5.copy_rates_from_pos(symbol, timeframe_code, 0, bars_count)
        
        if rates is None or len(rates) == 0:
            logger.log_error(f"Failed to fetch data for {timeframe_name}")
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        return df
    
    def update_df(self, timeframe_name):
        df = self.dataframes.get(timeframe_name)
        last_bar_time = self.last_bar_times.get(timeframe_name)
        
        new_data = self.fetch_data(timeframe_name)
        
        if new_data is None:
            return df, False
        
        new_last_bar = new_data['time'].iloc[-1]
        
        if df is None:
            self.dataframes[timeframe_name] = new_data
            self.last_bar_times[timeframe_name] = new_last_bar
            return new_data, True
        
        # commented out to make sure the latest bar is always included in the df, even if it has the same timestamp as the last bar in the existing df
        # uncomment only if previous candle data is needed and not the current forming candle data
        #  
        # if last_bar_time is not None and new_last_bar <= last_bar_time:
        #     return df, False
        
        bars_to_keep = config.get('trading', 'data_bars', timeframe_name)
        updated_df = pd.concat([df, new_data.tail(2)], ignore_index=True)
        updated_df = updated_df.drop_duplicates(subset=['time'], keep='last')
        updated_df = updated_df.tail(bars_to_keep).reset_index(drop=True)
        
        self.dataframes[timeframe_name] = updated_df
        self.last_bar_times[timeframe_name] = new_last_bar
        
        return updated_df, True
    
    def get_df(self, timeframe_name):
        return self.dataframes.get(timeframe_name)

data_fetcher = DataFetcher()
