import logging
from datetime import datetime
from pathlib import Path
from config_loader import config

class TradingLogger:
    def __init__(self):
        self.log_dir = Path(config.get('logging', 'log_directory'))
        self.date_str = datetime.now().strftime('%Y%m%d')
        
        self.trade_logger = self._setup_logger('trades', f'trades_{self.date_str}.log')
        self.system_logger = self._setup_logger('system', f'system_{self.date_str}.log')
    
    def _setup_logger(self, name, filename):
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, config.get('logging', 'log_level')))
        
        handler = logging.FileHandler(self.log_dir / filename)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)
        
        return logger
    
    def log_tp_sl_calculation(self, timestamp, tp, sl, adaptive_tp, adaptive_sl):
        msg = (
            f"LEVELS | {timestamp} | "
            f"TP: {tp:.2f} | SL: {sl:.2f} | "
            f"Adaptive TP: {adaptive_tp:.2f} | Adaptive SL: {adaptive_sl:.2f}"
        )
        self.trade_logger.info(msg)
    
    def log_trade_execution(self, timestamp, direction, entry, size, sl, tp, ttl):
        msg = (
            f"EXECUTE | {timestamp} | "
            f"{direction.upper()} | Entry: {entry:.2f} | "
            f"Size: {size:.2f} | SL: {sl:.2f} | TP: {tp:.2f} | TTL: {ttl} bars"
        )
        self.trade_logger.info(msg)
    
    def log_trade_exit(self, timestamp, exit_price, pnl, reason):
        msg = (
            f"EXIT | {timestamp} | "
            f"Price: {exit_price:.2f} | P&L: ${pnl:.2f} | Reason: {reason}"
        )
        self.trade_logger.info(msg)
    
    def log_drawdown_warning(self, current_dd_pct, limit_pct):
        msg = f"WARNING | Daily drawdown at {current_dd_pct:.2f}% (limit: {limit_pct:.2f}%)"
        self.risk_logger.warning(msg)
    
    def log_system_event(self, event_type, message):
        if not config.get('logging', 'log_system'):
            return
        
        msg = f"{event_type.upper()} | {message}"
        self.system_logger.info(msg)
    
    def log_error(self, error_msg):
        self.system_logger.error(error_msg)

logger = TradingLogger()
