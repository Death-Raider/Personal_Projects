import pandas as pd
from pathlib import Path
from config_loader import config

class CSVManager:
    def __init__(self):
        self.base_dir = Path(config.get('output', 'charts_base_directory'))
        self.csv_dir = Path(config.get('output', 'csv_directory'))
        
    def append_bar_data(self, timeframe, bar_data):
        csv_path: Path = self.base_dir / self.csv_dir / timeframe / 'historical_data.csv'
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        row_dict = {
            'timestamp': bar_data.get('time'),
            'open': bar_data.get('open'),
            'high': bar_data.get('high'),
            'low': bar_data.get('low'),
            'close': bar_data.get('close'),
            'tick_volume': bar_data.get('tick_volume'),
        }
        
        row_df = pd.DataFrame([row_dict])
        
        if csv_path.exists():
            row_df.to_csv(csv_path, mode='a', header=False, index=False)
        else:
            row_df.to_csv(csv_path, mode='w', header=True, index=False)

csv_manager = CSVManager()