import pandas as pd
import numpy as np
from config_loader import config

class SignalGenerator:
    def __init__(self):
        self.signal_history = []
        self.min_consecutive = config.get('signals', 'min_consecutive_bars')

    def calculate_metrics_corr(self, m5_data):
        new_df = []
        for row in m5_data['df'].itertuples():
            latest_m5 = pd.Series(row._asdict())
            
            m5_metrics = self.calculate_metrics(
                latest_m5,
                m5_data.get('vpoc'),
                m5_data.get('val'),
                m5_data.get('vah')
            )
            new_df.append(m5_metrics)
        new_df = pd.DataFrame(new_df)
        print(new_df)
        print(new_df.corr())
        return new_df
    
    def calculate_metrics(self, row, vpoc=None, val=None, vah=None):
        """
        Calculate INDEPENDENT signal metrics.
        Each component measures a different market aspect.
        Target correlation < 0.5 between components.
        """
        metrics = {}
        
        metrics['vp_position_score'] = self._calculate_vp_position_score_independent(row, vpoc, val, vah)
        metrics['order_flow_score'] = self._calculate_order_flow_score_independent(row)
        metrics['vwap_relation_score'] = self._calculate_vwap_relation_score_independent(row)
        metrics['liquidity_filter'] = self._calculate_liquidity_filter_smooth(row)
        metrics['vrp_filter'] = self._calculate_vrp_filter_smooth(row)
        
        vp_weight = config.get('signals', 'vp_score')
        flow_weight = config.get('signals', 'flow_score')
        vwap_weight = config.get('signals', 'vwap_score')
        
        metrics['raw_score'] = (
            metrics['vp_position_score'] * vp_weight +
            metrics['order_flow_score'] * flow_weight +
            metrics['vwap_relation_score'] * vwap_weight
        )
        
        metrics['filtered_score'] = (
            metrics['raw_score'] * 
            metrics['liquidity_filter'] * 
            metrics['vrp_filter']
        )
        
        return metrics
    
    def calculate_bias(self, df):
        if df is None or len(df) < 50:
            return 0.0
        return self._determine_bias_smooth(df)
    
    def generate_signal_mtf(self, market_data):
        if 'M5' not in market_data or market_data['M5']['df'] is None:
            return 0, 0.0, {}
        
        m5_data = market_data['M5']
        h1_data = market_data.get('H1', {})
        h4_data = market_data.get('H4', {})
        
        if len(m5_data['df']) < 50:
            return 0, 0.0, {}
        
        latest_m5 = m5_data['df'].iloc[-1]
        
        m5_metrics = self.calculate_metrics(
            latest_m5,
            m5_data.get('vpoc'),
            m5_data.get('val'),
            m5_data.get('vah')
        )
        
        mtf_multiplier = self._calculate_mtf_confluence_smooth(m5_data, h1_data, h4_data)
        
        m5_metrics['mtf_multiplier'] = mtf_multiplier
        m5_metrics['final_score'] = m5_metrics['filtered_score'] * mtf_multiplier
        
        components = {k: round(v, 2) for k, v in m5_metrics.items()}
        
        min_threshold = config.get('signals', 'min_confidence_score')
        
        if m5_metrics['final_score'] > min_threshold:
            signal = 1
            strength = min(m5_metrics['final_score'] / 100, 1.0)
        elif m5_metrics['final_score'] < -min_threshold:
            signal = -1
            strength = min(abs(m5_metrics['final_score']) / 100, 1.0)
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
        
        raw_signal = 0
        
        if er < 0.3:
            raw_signal = self._ranging_signal_legacy(latest, df)
        elif er > 0.6:
            raw_signal = self._trending_signal_legacy(latest, df)
        
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
    
    def _calculate_vp_position_score_independent(self, row, vpoc, val, vah):
        """
        PURE price structure - no order flow
        Measures ONLY: where price is in value area
        """
        if vpoc is None or val is None or vah is None:
            return 0.0
        
        price = row['close']
        va_width = vah - val
        
        if va_width == 0:
            return 0.0
        
        distance_from_vpoc_normalized = (price - vpoc) / va_width
        
        base_score = np.tanh(distance_from_vpoc_normalized * 2) * 70
        
        if price < val:
            extension_penalty = ((val - price) / va_width) * 30
            base_score -= extension_penalty
        elif price > vah:
            extension_penalty = ((price - vah) / va_width) * 30
            base_score += extension_penalty
        
        return np.clip(base_score, -100, 100)
    
    def _calculate_order_flow_score_independent(self, row):
        """
        PURE order flow - no price displacement
        Measures ONLY: buying vs selling pressure
        Uses ONLY delta and volume metrics
        """
        cum_delta = row.get('cumulative_delta', 0)
        vol_delta = row.get('volume_delta', 0)
        rel_vol = row.get('relative_volume', 1.0)
        
        persistent_flow = np.tanh(cum_delta / 10000) * 50
        
        current_bar_flow = np.tanh(vol_delta / 500) * 30
        
        volume_conviction = (rel_vol - 1.0) * 20
        volume_conviction = np.clip(volume_conviction, -20, 20)
        
        total_score = persistent_flow + current_bar_flow + volume_conviction
        
        return np.clip(total_score, -100, 100)
    
    def _calculate_vwap_relation_score_independent(self, row):
        """
        PURE institutional activity indicator
        Measures ONLY: deviation from VWAP in ATR terms + efficiency
        NO order flow, NO simple price displacement
        """
        price = row['close']
        vwap = row.get('vwap', price)
        atr = row.get('atr', price * 0.01)
        er = row.get('efficiency_ratio', 0.5)
        spread = row.get('spread_proxy', 0.01)
        
        if atr == 0:
            return 0.0
        
        distance_in_atr = (price - vwap) / atr
        
        deviation_score = np.tanh(distance_in_atr * 0.8) * 50
        
        trend_strength = (er - 0.5) * 2
        trend_multiplier = 1.0 + (trend_strength * 0.5)
        
        spread_quality = 1.0 - np.tanh((spread - 0.01) / 0.01) * 0.3
        spread_quality = np.clip(spread_quality, 0.7, 1.0)
        
        total_score = deviation_score * trend_multiplier * spread_quality
        
        return np.clip(total_score, -100, 100)
    
    def _calculate_liquidity_filter_smooth(self, row):
        """Smooth liquidity filter (0.3 to 1.0)"""
        illiq = row.get('amihud_illiquidity', 0.5)
        spread = row.get('spread_proxy', 0.01)
        
        illiq_penalty = np.tanh((illiq - 0.5) / 0.5) * 0.35
        spread_penalty = np.tanh((spread - 0.01) / 0.01) * 0.35
        
        filter_value = 1.0 - illiq_penalty - spread_penalty
        
        return np.clip(filter_value, 0.3, 1.0)
    
    def _calculate_vrp_filter_smooth(self, row):
        """Smooth VRP filter (0.5 to 1.0)"""
        vrp = row.get('vol_risk_premium', 0)
        
        penalty = abs(vrp) / 20
        penalty = np.clip(penalty, 0, 0.5)
        
        filter_value = 1.0 - penalty
        
        return np.clip(filter_value, 0.5, 1.0)
    
    def _calculate_mtf_confluence_smooth(self, m5_data, h1_data, h4_data):
        """Smooth MTF multiplier (0.5 to 2.0)"""
        if not h1_data or not h4_data:
            return 1.0
        
        h1_bias_score = self._determine_bias_smooth(h1_data.get('df'))
        h4_bias_score = self._determine_bias_smooth(h4_data.get('df'))
        
        alignment = (h1_bias_score * h4_bias_score + 1) / 2
        
        multiplier = 0.5 + (alignment * 1.5)
        
        return np.clip(multiplier, 0.5, 2.0)
    
    def _determine_bias_smooth(self, df):
        """Returns continuous bias score (-1 to +1)"""
        if df is None or len(df) < 50:
            return 0.0
        
        latest = df.iloc[-1]
        cum_delta = latest.get('cumulative_delta', 0)
        er = latest.get('efficiency_ratio', 0.5)
        
        delta_bias = np.tanh(cum_delta / 10000)
        er_weight = np.clip(er, 0, 1)
        final_bias = delta_bias * er_weight
        
        return np.clip(final_bias, -1.0, 1.0)
    
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