import pandas as pd
import numpy as np
from config_loader import config

class IncrementalMetricsCalculator:
    def __init__(self):
        self.metrics = [
            "vwap",
            "volume_delta",
            "cumulative_delta",
            "relative_volume",
            "realized_vol",
            "atr",
            "implied_vol",
            "vol_risk_premium",
            "spread_proxy",
            "amihud_illiquidity",
            "efficiency_ratio",
        ]

    def _get_increment_condition(self,df:pd.DataFrame):
        """
                MC
        IC    0    1
        0   Full  -
        1     -   Inc
        """
        metrics_condition = all(metric in df.columns for metric in self.metrics) # MC
        increment_condition = False # IC
        if metrics_condition:
            increment_condition = any(df.iloc[-2:][metric].isna().sum() > 0 for metric in self.metrics)
        return metrics_condition, increment_condition

    def calculate_all_metrics(self, df, timeframe, constant_df=True):
        if df is None or len(df) == 0:
            return df
                
        metrics_condition,increment_condition = self._get_increment_condition(df)
        if not metrics_condition:
            print("Calculating all metrics from scratch...")
            df = self._calculate_full(df)
        else:
            if increment_condition:
                print("Calculating metrics incrementally...")
                df = self._calculate_incremental(df)
            else:
                print("All metrics already calculated, skipping...")
        
        return df
    
    def _calculate_full(self, df):
        period_20 = 20
        period_100 = 100
        period_14 = 14
        df = self._add_volume_metrics(df,[period_100, period_20])
        df = self._add_volatility_metrics(df, period_20)
        df = self._add_liquidity_metrics(df, period_20)
        return df
    
    def _calculate_incremental(self, df):
        period_20 = 20
        period_100 = 100
        period_14 = 14
        
        required_lookback = -2 - 100 # -2 for rows which are NAN, -100 for cumulative delta rolling sum
        
        subset = df.iloc[required_lookback:].copy()
        subset = self._add_volume_metrics(subset, [period_100, period_20])
        subset = self._add_volatility_metrics(subset, period_20)
        subset = self._add_liquidity_metrics(subset, period_20)
        
        new_data = subset.iloc[required_lookback:]
        df.iloc[required_lookback:, df.columns.get_indexer(new_data.columns)] = new_data.values
        
        return df
    
    def _add_volume_metrics(self, df, rolling_window: int|list[int]=20):
        if type(rolling_window) == int:
            rolling_window = [rolling_window, rolling_window]
        df['vwap'] = self._calculate_vwap(df)
        df['volume_delta'] = self._calculate_volume_delta(df)
        df['cumulative_delta'] = df['volume_delta'].rolling(rolling_window[0], min_periods=1).sum()
        
        avg_vol = df['tick_volume'].rolling(rolling_window[1], min_periods=1).mean()
        df['relative_volume'] = df['tick_volume'] / avg_vol.replace(0, 1)
        
        return df
    
    def _calculate_vwap(self, df):
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        tp_volume = typical_price * df['tick_volume']
        vwap = tp_volume.rolling(20, min_periods=1).sum() / df['tick_volume'].rolling(20, min_periods=1).sum()
        return vwap
    
    def _calculate_volume_delta(self, df):
        delta = pd.Series(index=df.index, dtype=float)
        
        for idx in df.index:
            row = df.loc[idx]
            price_range = row['high'] - row['low']
            if price_range == 0:
                close_pct = 0.5
            else:
                close_pct = (row['close'] - row['low']) / price_range
            
            delta.loc[idx] = (close_pct - 0.5) * 2 * row['tick_volume']
        
        return delta
    
    def _add_volatility_metrics(self, df, rolling_window=20):
        annualization_factor = 105120
        
        log_returns = np.log(df['close'] / df['close'].shift(1))
        df['realized_vol'] = log_returns.rolling(rolling_window, min_periods=1).std() * np.sqrt(annualization_factor) * 100
        
        df['atr'] = self._calculate_atr(df, period=14)
        avg_price = df['close'].rolling(14, min_periods=1).mean()
        df['implied_vol'] = (df['atr'] / avg_price) * np.sqrt(annualization_factor) * 100
        
        df['vol_risk_premium'] = df['implied_vol'] - df['realized_vol']
        
        return df
    
    def _calculate_atr(self, df, period=14):
        high = df['high']
        low = df['low']
        close = df['close']
        prev_close = close.shift(1)
        
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.ewm(span=period, adjust=False, min_periods=period).mean()
        
        return atr
    
    def _add_liquidity_metrics(self, df, rolling_window=20):
        hl_ratio = np.log(df['high'] / df['low'].replace(0, 1))
        df['spread_proxy'] = 2 * np.sqrt((hl_ratio**2).rolling(rolling_window, min_periods=1).mean())
        
        returns = df['close'].pct_change().abs()
        volume = df['tick_volume'].replace(0, 1)
        df['amihud_illiquidity'] = (returns / volume).rolling(rolling_window, min_periods=1).mean() * 1e6
        
        direction = df['close'].diff(rolling_window).abs()
        volatility = df['close'].diff().abs().rolling(rolling_window, min_periods=1).sum()
        df['efficiency_ratio'] = direction / volatility.replace(0, 1)
        
        return df
    
    def calculate_volume_profile(self, df, lookback=500):
        if lookback <= 0:
            lookback = config.get('volumen_profile', 'lookback_bars')
            
        if len(df) < lookback:
            lookback = len(df)
        
        recent_df = df.tail(lookback).copy()
        
        price_min = recent_df['low'].min()
        price_max = recent_df['high'].max()
        bins = config.get('volume_profile', 'price_bins')
        price_bins = np.linspace(price_min, price_max, bins)
        
        volume_at_price = np.zeros(len(price_bins) - 1)
        
        for idx, row in recent_df.iterrows():
            candle_bins = np.digitize([row['low'], row['high']], price_bins)
            affected_bins = range(max(0, candle_bins[0]-1), min(len(price_bins)-1, candle_bins[1]))
            
            vol_per_bin = row['tick_volume'] / max(1, len(affected_bins))
            for bin_idx in affected_bins:
                volume_at_price[bin_idx] += vol_per_bin
        
        profile_df = pd.DataFrame({
            'price_level': (price_bins[:-1] + price_bins[1:]) / 2,
            'volume': volume_at_price,
        })
        
        total_volume = profile_df['volume'].sum()
        profile_df['volume_pct'] = (profile_df['volume'] / total_volume) * 100
        
        sorted_profile = profile_df.sort_values('volume', ascending=False)
        sorted_profile['cumsum_pct'] = sorted_profile['volume_pct'].cumsum()
        
        vpoc = sorted_profile.iloc[0]['price_level']
        
        value_area_pct = config.get('volume_profile', 'value_area_pct')
        value_area = sorted_profile[sorted_profile['cumsum_pct'] <= value_area_pct]
        
        if len(value_area) == 0:
            val = profile_df['price_level'].min()
            vah = profile_df['price_level'].max()
        else:
            val = value_area['price_level'].min()
            vah = value_area['price_level'].max()
        
        return profile_df, vpoc, val, vah

metrics_calculator = IncrementalMetricsCalculator()
