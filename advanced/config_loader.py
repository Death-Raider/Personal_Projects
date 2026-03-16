import json
import os
from pathlib import Path

class Config:
    _instance = None
    _config = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, path='config.json'):
        if self._config is None:
            self.load_config(path, directory=os.path.dirname(path))
    
    def load_config(self, path='config.json', directory=None):
        with open(path, 'r') as f:
            self._config = json.load(f)
        
        self._ensure_directories(directory)
    
    def _ensure_directories(self, directory):
        Path(self._config['logging']['log_directory']).mkdir(exist_ok=True)
        (Path(self._config['output']['charts_base_directory']) / Path(self._config['output']['csv_directory'])).mkdir(exist_ok=True)
        
        for tf in self._config['trading']['timeframes'].keys():
            Path(os.path.join(directory, tf)).mkdir(exist_ok=True)
    
    def get(self, *keys):
        value = self._config
        for key in keys:
            value = value[key]
        return value
    
    def set(self, value, *keys):
        target = self._config
        for key in keys[:-1]:
            target = target[key]
        target[keys[-1]] = value
    
    def save(self, path='config.json'):
        with open(path, 'w') as f:
            json.dump(self._config, f, indent=2)

config = Config("advanced/config.json")
