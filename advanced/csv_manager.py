import pandas as pd
from pathlib import Path
from datetime import datetime
from config_loader import config


class CSVManager:
    """
    Manages all CSV persistence.

    Files written (all under charts_base_directory/csv_directory/<timeframe>/):
        historical_data.csv   — bar-by-bar OHLCV (appended every bar)
        trades.csv            — one row per closed trade
        session_stats.csv     — one row per regime change (stats snapshot)
    """

    def __init__(self):
        self.base_dir = Path(config.get('output', 'charts_base_directory'))
        self.csv_dir  = Path(config.get('output', 'csv_directory'))

    # ── Internal ──────────────────────────────────────────────────────

    def _path(self, timeframe: str, filename: str) -> Path:
        p = self.base_dir / self.csv_dir / timeframe / filename
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def _append_row(self, path: Path, row: dict):
        df = pd.DataFrame([row])
        write_header = not path.exists()
        df.to_csv(path, mode='a', header=write_header, index=False)

    # ── Bar data ──────────────────────────────────────────────────────

    def append_bar_data(self, timeframe: str, bar_data: dict):
        """Append one OHLCV bar row. Called every new bar."""
        path = self._path(timeframe, 'historical_data.csv')
        row  = {
            'timestamp'  : bar_data.get('time'),
            'open'       : bar_data.get('open'),
            'high'       : bar_data.get('high'),
            'low'        : bar_data.get('low'),
            'close'      : bar_data.get('close'),
            'tick_volume': bar_data.get('tick_volume'),
        }
        self._append_row(path, row)

    def load_bar_data(self, timeframe: str) -> pd.DataFrame:
        path = self._path(timeframe, 'historical_data.csv')
        if not path.exists():
            return pd.DataFrame()
        return pd.read_csv(path, parse_dates=['timestamp'])

    # ── Trade log ─────────────────────────────────────────────────────

    def log_trade(self, timeframe: str, trade: dict):
        """
        Append one closed trade to trades.csv.
        Called by position_manager.close_position on every exit.
        """
        path = self._path(timeframe, 'trades.csv')
        row  = {
            'logged_at'    : datetime.now().isoformat(),
            'position_id'  : trade.get('position_id'),
            'direction'    : trade.get('direction'),
            'entry_price'  : trade.get('entry_price'),
            'exit_price'   : trade.get('exit_price'),
            'entry_time'   : trade.get('entry_time'),
            'exit_time'    : trade.get('exit_time'),
            'pnl_points'   : trade.get('pnl_points'),
            'outcome'      : trade.get('outcome'),
            'bars_in_trade': trade.get('bars_in_trade'),
            'entry_p_tp'   : trade.get('entry_p_tp'),
            'entry_edge'   : trade.get('entry_edge'),
            'surface_id'   : trade.get('surface_id'),
            'mu'           : trade.get('mu'),
        }
        self._append_row(path, row)

    def load_trades(self, timeframe: str) -> pd.DataFrame:
        path = self._path(timeframe, 'trades.csv')
        if not path.exists():
            return pd.DataFrame()
        return pd.read_csv(path)

    # ── Session stats ─────────────────────────────────────────────────

    def log_session_stats(self, timeframe: str, stats: dict):
        """
        Append a performance snapshot to session_stats.csv.
        Called by position_manager.log_stats_on_regime_change
        every time the PDE surface is recomputed.
        """
        path = self._path(timeframe, 'session_stats.csv')
        row  = {
            'logged_at'    : datetime.now().isoformat(),
            'timestamp'    : stats.get('timestamp'),
            'surface_id'   : stats.get('surface_id'),
            'sigma_bar'    : stats.get('sigma_bar'),
            'sigma0'       : stats.get('sigma0'),
            'mu'           : stats.get('mu'),
            'total_trades' : stats.get('total_trades'),
            'win_pct'      : stats.get('win_pct'),
            'total_pnl'    : stats.get('total_pnl'),
            'sharpe'       : stats.get('sharpe'),
            'max_drawdown' : stats.get('max_drawdown'),
            'calmar'       : stats.get('calmar'),
        }
        self._append_row(path, row)

    def load_session_stats(self, timeframe: str) -> pd.DataFrame:
        path = self._path(timeframe, 'session_stats.csv')
        if not path.exists():
            return pd.DataFrame()
        return pd.read_csv(path)


csv_manager = CSVManager()