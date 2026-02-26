import pandas as pd
import numpy as np
from config_loader import config

class SignalGenerator:
    def __init__(self):
        self.signal_history = []
        self.min_consecutive = config.get('signals', 'min_consecutive_bars')
    
    def generate_signal_mtf(self, market_data):
        if 'M5' not in market_data or market_data['M5']['df'] is None:
            return 0, 0.0, {}
        
        m5_data = market_data['M5']
        h1_data = market_data.get('H1', {})
        h4_data = market_data.get('H4', {})
        
        if len(m5_data['df']) < 50:
            return 0, 0.0, {}
        
        latest_m5 = m5_data['df'].iloc[-1]
        
        vp_score = self._calculate_vp_position_score(
            latest_m5, 
            m5_data.get('vpoc'), 
            m5_data.get('val'), 
            m5_data.get('vah')
        )
        
        flow_score = self._calculate_order_flow_score(latest_m5)
        
        vwap_score = self._calculate_vwap_relation_score(latest_m5)
        
        raw_score = (
            vp_score * config.get('signals', 'vp_score') +
            flow_score * config.get('signals', 'flow_score') +
            vwap_score * config.get('signals', 'vwap_score')
        )
        
        liquidity_filter = self._calculate_liquidity_filter(latest_m5)
        vrp_filter = self._calculate_vrp_filter(latest_m5)
        
        mtf_multiplier = self._calculate_mtf_confluence(m5_data, h1_data, h4_data)
        
        filtered_score = raw_score * liquidity_filter * vrp_filter * mtf_multiplier
        
        components = {
            'vp_position_score': round(vp_score, 2),
            'order_flow_score': round(flow_score, 2),
            'vwap_relation_score': round(vwap_score, 2),
            'raw_score': round(raw_score, 2),
            'liquidity_filter': round(liquidity_filter, 3),
            'vrp_filter': round(vrp_filter, 3),
            'mtf_multiplier': round(mtf_multiplier, 2),
            'filtered_score': round(filtered_score, 2)
        }
        
        if filtered_score > config.get('signals', 'min_confidence_score'):
            signal = 1
            strength = min(filtered_score / 100, 1.0)
        elif filtered_score < -config.get('signals', 'min_confidence_score'):
            signal = -1
            strength = min(abs(filtered_score) / 100, 1.0)
        else:
            signal = 0
            strength = 0.0
        
        self.signal_history.append(signal)
        if len(self.signal_history) > 10:
            self.signal_history.pop(0)
        
        if len(self.signal_history) < self.min_consecutive:
            return 0, 0.0, components
        
        last_n = self.signal_history[-self.min_consecutive:]
        
        if all(s == signal and s != 0 for s in last_n):
            rel_vol = latest_m5.get('relative_volume', 0)
            if rel_vol >= config.get('signals', 'min_relative_volume'):
                return signal, strength, components
        
        return 0, 0.0, components
    
    def generate_signal(self, df):
        if len(df) < 50:
            return 0
        
        latest = df.iloc[-1]
        
        er = latest.get('efficiency_ratio', 0.5)
        rel_vol = latest.get('relative_volume', 1.0)
        cum_delta = latest.get('cumulative_delta', 0)
        
        raw_signal = 0
        
        if er < 0.3:
            raw_signal = self._ranging_signal_legacy(latest, df)
        elif er > 0.6:
            raw_signal = self._trending_signal_legacy(latest, df)
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
    
    def _calculate_vp_position_score(self, row, vpoc, val, vah):
        if vpoc is None or val is None or vah is None:
            return 0
        
        price = row['close']
        cum_delta = row.get('cumulative_delta', 0)
        rel_vol = row.get('relative_volume', 1.0)
        
        va_width = vah - val
        if va_width == 0:
            return 0
        
        score = 0
        
        if price <= val:
            if cum_delta > 5000 and rel_vol > 1.2:
                score = 80
            elif cum_delta > 0:
                score = 50
            else:
                score = 20
        elif price >= vah:
            if cum_delta < -5000 and rel_vol > 1.2:
                score = -80
            elif cum_delta < 0:
                score = -50
            else:
                score = -20
        else:
            distance_from_vpoc = (price - vpoc) / va_width
            score = distance_from_vpoc * 40
        
        return score
    
    def _calculate_order_flow_score(self, row):
        cum_delta = row.get('cumulative_delta', 0)
        vol_delta = row.get('volume_delta', 0)
        rel_vol = row.get('relative_volume', 1.0)
        
        if abs(cum_delta) > 10000:
            base_score = 90 if cum_delta > 0 else -90
        elif abs(cum_delta) > 5000:
            base_score = 70 if cum_delta > 0 else -70
        elif abs(cum_delta) > 2000:
            base_score = 50 if cum_delta > 0 else -50
        else:
            base_score = 20 if cum_delta > 0 else -20
        
        if rel_vol > 1.5:
            score = base_score
        elif rel_vol > 1.0:
            score = base_score * 0.8
        else:
            score = base_score * 0.5
        
        return score
    
    def _calculate_vwap_relation_score(self, row):
        price = row['close']
        vwap = row.get('vwap', price)
        atr = row.get('atr', price * 0.01)
        cum_delta = row.get('cumulative_delta', 0)
        rel_vol = row.get('relative_volume', 1.0)
        
        if atr == 0:
            return 0
        
        distance = (price - vwap) / atr
        
        if distance > 1.0:
            if cum_delta > 5000 and rel_vol > 1.2:
                score = 85
            elif cum_delta > 0:
                score = 60
            else:
                score = 30
        elif distance < -1.0:
            if cum_delta < -5000 and rel_vol > 1.2:
                score = -85
            elif cum_delta < 0:
                score = -60
            else:
                score = -30
        else:
            score = distance * 50
        
        return score
    
    def _calculate_liquidity_filter(self, row):
        illiq = row.get('amihud_illiquidity', 0.5)
        spread = row.get('spread_proxy', 0.01)
        
        if illiq < 0.3 and spread < 0.01:
            return 1.0
        elif illiq > 1.0 or spread > 0.02:
            return 0.3
        else:
            return 0.7
    
    def _calculate_vrp_filter(self, row):
        vrp = row.get('vol_risk_premium', 0)
        
        if abs(vrp) > 15:
            return 0.5
        elif abs(vrp) > 10:
            return 0.7
        else:
            return 1.0
    
    def _calculate_mtf_confluence(self, m5_data, h1_data, h4_data):
        if not h1_data or not h4_data:
            return 1.0
        
        h1_regime = h1_data.get('regime', 'neutral')
        h4_regime = h4_data.get('regime', 'neutral')
        
        h1_bias = self._determine_bias(h1_data.get('df'))
        h4_bias = self._determine_bias(h4_data.get('df'))
        
        if h4_bias == h1_bias and h4_bias != 'neutral':
            return 2.0
        elif h4_bias != 'neutral' and h1_bias == 'neutral':
            return 1.5
        elif h4_bias == 'neutral' and h1_bias == 'neutral':
            return 1.0
        else:
            return 0.5
    
    def _determine_bias(self, df):
        if df is None or len(df) < 50:
            return 'neutral'
        
        latest = df.iloc[-1]
        cum_delta = latest.get('cumulative_delta', 0)
        er = latest.get('efficiency_ratio', 0.5)
        
        if cum_delta > 8000 and er > 0.5:
            return 'bullish'
        elif cum_delta < -8000 and er > 0.5:
            return 'bearish'
        else:
            return 'neutral'
    
    def _ranging_signal_legacy(self, latest, df):
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
    
    def _trending_signal_legacy(self, latest, df):
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