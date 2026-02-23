import pandas as pd
from config_loader import config

class SignalGenerator:
    def __init__(self):
        self.signal_history = []
        self.min_consecutive = config.get('signals', 'min_consecutive_bars')
    
    def generate_signal(self, df):
        if len(df) < 50:
            return 0
        
        latest = df.iloc[-1]
        
        er = latest.get('efficiency_ratio', 0.5)
        rel_vol = latest.get('relative_volume', 1.0)
        cum_delta = latest.get('cumulative_delta', 0)
        vrp = latest.get('vol_risk_premium', 0)
        
        raw_signal = 0
        
        if er < 0.3:
            raw_signal = self._ranging_signal(latest, df)
        elif er > 0.6:
            raw_signal = self._trending_signal(latest, df)
        else:
            raw_signal = 0
        
        self.signal_history.append(raw_signal)
        if len(self.signal_history) > 10:
            self.signal_history.pop(0)
        
        if len(self.signal_history) < self.min_consecutive:
            return 0
        
        last_n = self.signal_history[-self.min_consecutive:]
        
        if all(s == raw_signal and s != 0 for s in last_n):
            if rel_vol >= config.get('signals', 'min_relative_volume'):
                return raw_signal
        
        return 0
    
    def _ranging_signal(self, latest, df):
        if len(df) < 100:
            return 0
        
        recent = df.tail(100)
        vpoc = recent['close'].median()
        val = recent['close'].quantile(0.25)
        vah = recent['close'].quantile(0.75)
        
        price = latest['close']
        cum_delta = latest.get('cumulative_delta', 0)
        
        if price >= vah and cum_delta < -3000:
            return -1
        elif price <= val and cum_delta > 3000:
            return 1
        
        return 0
    
    def _trending_signal(self, latest, df):
        if len(df) < 50:
            return 0
        
        sma_20 = df['close'].tail(20).mean()
        sma_50 = df['close'].tail(50).mean()
        
        price = latest['close']
        cum_delta = latest.get('cumulative_delta', 0)
        
        if sma_20 > sma_50 and price > sma_20 and cum_delta > 5000:
            return 1
        elif sma_20 < sma_50 and price < sma_20 and cum_delta < -5000:
            return -1
        
        return 0

signal_generator = SignalGenerator()
