import pandas as pd
from pathlib import Path
from config_loader import config
from signal_generator import signal_generator

class CSVManager:
    def __init__(self):
        self.base_dir = Path(config.get('output', 'charts_base_directory'))
        
    def append_bar_data(self, timeframe, bar_data, vpoc, val, vah, regime, signal):
        csv_path = self.base_dir / timeframe / 'historical_data.csv'
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        metrics = signal_generator.calculate_metrics(bar_data, vpoc, val, vah)
        
        bias_score = 0.0
        if timeframe in ['H1', 'H4']:
            bias_score = signal_generator._determine_bias_smooth(None)
        
        row_dict = {
            'timestamp': bar_data.get('time'),
            'open': bar_data.get('open'),
            'high': bar_data.get('high'),
            'low': bar_data.get('low'),
            'close': bar_data.get('close'),
            'tick_volume': bar_data.get('tick_volume'),
            'vwap': bar_data.get('vwap'),
            'volume_delta': bar_data.get('volume_delta'),
            'cumulative_delta': bar_data.get('cumulative_delta'),
            'relative_volume': bar_data.get('relative_volume'),
            'realized_vol': bar_data.get('realized_vol'),
            'atr': bar_data.get('atr'),
            'implied_vol': bar_data.get('implied_vol'),
            'vol_risk_premium': bar_data.get('vol_risk_premium'),
            'amihud_illiquidity': bar_data.get('amihud_illiquidity'),
            'spread_proxy': bar_data.get('spread_proxy'),
            'efficiency_ratio': bar_data.get('efficiency_ratio'),
            'vpoc': vpoc,
            'val': val,
            'vah': vah,
            'regime': regime,
            'signal': signal,
            'vp_position_score': metrics.get('vp_position_score'),
            'order_flow_score': metrics.get('order_flow_score'),
            'vwap_relation_score': metrics.get('vwap_relation_score'),
            'liquidity_filter': metrics.get('liquidity_filter'),
            'vrp_filter': metrics.get('vrp_filter'),
            'raw_score': metrics.get('raw_score'),
            'filtered_score': metrics.get('filtered_score'),
            'bias_score': bias_score
        }
        
        row_df = pd.DataFrame([row_dict])
        
        if csv_path.exists():
            row_df.to_csv(csv_path, mode='a', header=False, index=False)
        else:
            row_df.to_csv(csv_path, mode='w', header=True, index=False)

csv_manager = CSVManager()