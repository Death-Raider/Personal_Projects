"""
position_manager.py
====================
Handles all live position state and MT5 order operations.

Key design rules
----------------
- ONE position active at a time (enforced in create_position)
- Entry decision comes from signal_gen.try_enter_trade — same code
  used by the backtest, no duplication
- SL/TP updates use the existing config-driven trailing logic
- MT5 order placement / modification / close all live here
- Stats (Sharpe, DD, Calmar, win%) computed on demand and on each
  regime change, written to csv_manager
"""

import numpy as np
import pandas as pd
from datetime import datetime

import MetaTrader5 as mt5
import time
from config_loader import config
from logger import logger
from csv_manager import csv_manager
# from signal_gen import try_enter_trade          # exact same entry logic as backtest

def try_enter_trade(bar_idx, df, surface, sigma_now, mu_now, p_base):
    """
    Placeholder for the actual entry logic, which lives in signal_gen.py.
    We import it here to avoid circular imports, since signal_gen needs
    to call position_manager.evaluate_entry from the backtest loop.
    """
    return True

replacements = {
    'µ': 'mu',
    'σ': 'sigma',
    'Σ': 'Sigma',
    'π': 'pi',
    'α': 'alpha',
    'β': 'beta',
    'γ': 'gamma',
    'δ': 'delta',
    'ε': 'epsilon',
    'θ': 'theta',
    'λ': 'lambda',
    'ρ': 'rho',
    'τ': 'tau',
    'φ': 'phi',
    'ω': 'omega',
}

def replace_special(text):
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text

def compute_stats(closed_trades: list) -> dict:
    """
    Compute Sharpe, max drawdown, Calmar, win-rate from a list of
    closed trade dicts.  Each dict must have 'pnl_points' and 'outcome'.
    Called periodically and on every regime change.
    """
    if not closed_trades:
        return {}

    pnls     = np.array([t.get('pnl_points', 0.0) for t in closed_trades])
    outcomes = [t.get('outcome', '') for t in closed_trades]
    n        = len(pnls)
    n_tp     = sum(1 for o in outcomes if o == 'TP')

    win_pct   = n_tp / n
    total_pnl = float(pnls.sum())
    avg_pnl   = float(pnls.mean())
    std_pnl   = float(pnls.std()) + 1e-9
    sharpe    = avg_pnl / std_pnl * np.sqrt(n)

    cum      = np.cumsum(pnls)
    run_max  = np.maximum.accumulate(cum)
    dd       = cum - run_max
    max_dd   = float(dd.min())
    calmar   = total_pnl / abs(max_dd) if max_dd != 0 else 0.0

    return dict(
        total_trades = n,
        win_pct      = win_pct,
        total_pnl    = total_pnl,
        avg_pnl      = avg_pnl,
        sharpe       = sharpe,
        max_drawdown = max_dd,
        calmar       = calmar,
    )


# ══════════════════════════════════════════════════════════════════════════════
# POSITION MANAGER
# ══════════════════════════════════════════════════════════════════════════════

class PositionManager:

    def __init__(self):
        # Single active position stored as dict keyed by position_id
        # Max 1 entry enforced by create_position
        self.active_positions: dict = {}

        # Full history of closed trades for stats
        self.closed_trades: list = []

    # ── Convenience ───────────────────────────────────────────────────────────

    def get_active_position(self):
        if not self.active_positions:
            return None
        pos_key = list(self.active_positions.keys())[0]
        position = mt5.positions_get(ticket=self.active_positions[pos_key]['mt5_ticket'])
        if not position:
            print("No open position with this ticket.")
            if pos_key in self.active_positions:
                del self.active_positions[pos_key]
            return None
        return list(self.active_positions.values())[0]

    def has_position(self) -> bool:
        return len(self.active_positions) > 0

    # ── ENTRY  (uses try_enter_trade from signal_gen — identical to backtest) ─

    def evaluate_entry(self, bar_idx: int, df: pd.DataFrame,
                        surface: dict, sigma_now: float,
                        mu_now: float, p_base) -> dict:
        """
        Calls signal_gen.try_enter_trade with the exact same arguments
        the backtest uses.  Returns the decision dict unchanged.
        The caller decides whether to act on decision['enter'].
        """
        return try_enter_trade(
            bar_idx   = bar_idx,
            df        = df,
            surface   = surface,
            sigma_now = sigma_now,
            mu_now    = mu_now,
            p_base    = p_base,
        )

    # ── CREATE POSITION  ──────────────────────────────────────────────────────

    def create_position(self, entry_decision: dict,
                         entry_time: datetime) -> dict | None:
        """
        Enforce single-position rule and build the internal position dict.
        Does NOT place an MT5 order — call place_mt5_order separately.

        Parameters
        ----------
        entry_decision  : dict returned by evaluate_entry / try_enter_trade
                          must contain: enter, direction, entry_price,
                          tp_distance, sl_distance, position_size
        entry_time      : datetime of this bar

        Returns None if a position is already active or enter=False.
        """
        if self.has_position():
            logger.log_error('create_position blocked: position already active')
            return None

        if not entry_decision.get('enter'):
            return None

        entry_price = entry_decision['entry_price']
        direction   = entry_decision['direction']
        tp_dist     = entry_decision['tp_distance']
        sl_dist     = entry_decision['sl_distance']

        if direction == 'long':
            stop_price   = round(entry_price - sl_dist, 2)
            target_price = round(entry_price + tp_dist, 2)
        else:
            stop_price   = round(entry_price + sl_dist, 2)
            target_price = round(entry_price - tp_dist, 2)

        position_id = f"{direction}_{entry_time.strftime('%Y%m%d_%H%M%S')}"

        position = {
            'id'                      : position_id,
            'direction'               : direction,
            'signal'                  : entry_decision.get('reason', 'NA'), 
            'entry_price'             : entry_price,
            'entry_time'              : entry_time,
            'size'                    : entry_decision.get('position_size', 0.1),
            'initial_stop'            : stop_price,
            'current_stop'            : stop_price,
            'initial_target'          : target_price,
            'current_target'          : target_price,
            'sl_distance_initial'     : sl_dist,
            'tp_distance_initial'     : tp_dist,
            'bars_in_trade'           : 0,
            'highest_price'           : entry_price,
            'lowest_price'            : entry_price,
            'max_favorable_excursion' : 0.0,
            'max_adverse_excursion'   : 0.0,
            'sl_updates'              : [],
            'tp_updates'              : [],
            # PDE metadata from the entry decision
            'entry_p_tp'              : entry_decision.get('p_tp_entry'),
            'entry_edge'              : entry_decision.get('edge'),
            'surface_id'              : entry_decision.get('surface_id'),
            'mu'                      : entry_decision.get('mu_now'),
            'mt5_ticket'              : None,   # filled after MT5 order
        }

        self.active_positions[position_id] = position

        logger.log_system_event('position_created',
            f"{direction.upper()} @ {entry_price:.2f}  "
            f"SL={stop_price:.2f}  TP={target_price:.2f}  "
            f"signal={position['signal']}")

        return position

    # ── MT5 ORDER OPERATIONS ──────────────────────────────────────────────────

    def place_mt5_order(self, position_id: str, retry=0) -> bool:
        """
        Send a market order to MT5 for the given position_id.
        Fills position['mt5_ticket'] and updates entry_price to fill price.
        Returns True on success.
        """
        position = self.active_positions.get(position_id)
        if position is None:
            logger.log_error(f'place_mt5_order: position {position_id} not found')
            return False

        symbol    = config.get('trading', 'symbol')
        direction = position['direction']
        size      = float(position['size']) if position['size'] else 0.01
        sl        = float(position['current_stop'])
        tp        = float(position['current_target'])

        order_type = (mt5.ORDER_TYPE_BUY
                      if direction == 'long'
                      else mt5.ORDER_TYPE_SELL)

        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            logger.log_error(f'place_mt5_order: no tick for {symbol}')
            return False

        request = {
            'action'      : mt5.TRADE_ACTION_DEAL,
            'symbol'      : symbol,
            'volume'      : size,
            'type'        : order_type,
            'price'       : tick.ask if direction == 'long' else tick.bid,
            'sl'          : sl,
            'tp'          : tp,
            'deviation'   : 10,
            'magic'       : 2340001,
            'comment'     : replace_special(position['signal'][:31]),
            'type_time'   : mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result:
            print("Retcode:", result.retcode)
            print("Comment:", result.comment)
        else:
            print("Last error:", mt5.last_error())

        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            code = result.retcode if result else 'None'
            logger.log_error(f'place_mt5_order failed: retcode={code}')
            print(request)
            print("MT5 returned None, retrying...")
            print("Last error:", mt5.last_error())

            mt5.shutdown()
            mt5.initialize()
            time.sleep(0.5)
            
            return self.place_mt5_order(position_id, retry=retry+1) if retry < 3 else None

        position['mt5_ticket']  = result.order
        position['entry_price'] = result.price   # actual fill price

        logger.log_trade_execution(
            timestamp = position['entry_time'],
            direction = direction,
            entry     = result.price,
            size      = size,
            sl        = sl,
            tp        = tp,
            ttl       = -1,
        )
        return True

    def modify_sl_mt5(self, position_id: str, new_sl: float) -> bool:
        """
        Modify stop loss on MT5 and update internal state.
        Only tightens SL — never widens it.
        """
        position = self.active_positions.get(position_id)
        if position is None:
            return False

        # Enforce tighten-only
        current_sl = position['current_stop']
        direction  = position['direction']
        if direction == 'long'  and new_sl <= current_sl:
            return False
        if direction == 'short' and new_sl >= current_sl:
            return False

        symbol = config.get('trading', 'symbol')
        ticket = position.get('mt5_ticket')

        if ticket is not None:
            request = {
                'action'  : mt5.TRADE_ACTION_SLTP,
                'symbol'  : symbol,
                'position': ticket,
                'sl'      : float(new_sl),
                'tp'      : float(position['current_target']),
            }
            result = mt5.order_send(request)

            if not (result and result.retcode == mt5.TRADE_RETCODE_DONE):
                logger.log_error(f'modify_sl_mt5 failed: '
                                  f'{result.retcode if result else "None"}')
                return False

        position['sl_updates'].append({
            'bar'    : position['bars_in_trade'],
            'old_sl' : current_sl,
            'new_sl' : new_sl,
            'reason' : 'trailing',
        })
        position['current_stop'] = round(new_sl, 2)
        logger.log_system_event('sl_modified',
            f"SL {current_sl:.2f} → {new_sl:.2f}")
        return True

    def modify_tp_mt5(self, position_id: str, new_tp: float) -> bool:
        """Modify take profit on MT5 and update internal state."""
        position = self.active_positions.get(position_id)
        if position is None:
            return False

        symbol = config.get('trading', 'symbol')
        ticket = position.get('mt5_ticket')

        if ticket is not None:
            request = {
                'action'  : mt5.TRADE_ACTION_SLTP,
                'symbol'  : symbol,
                'position': ticket,
                'sl'      : float(position['current_stop']),
                'tp'      : float(new_tp),
            }
            result = mt5.order_send(request)

            if not (result and result.retcode == mt5.TRADE_RETCODE_DONE):
                logger.log_error(f'modify_tp_mt5 failed: '
                                  f'{result.retcode if result else "None"}')
                return False

        old_tp = position['current_target']
        position['tp_updates'].append({
            'bar'    : position['bars_in_trade'],
            'old_tp' : old_tp,
            'new_tp' : new_tp,
        })
        position['current_target'] = round(new_tp, 2)
        return True

    def close_position(self, position_id: str,
                        exit_price: float,
                        exit_reason: str,
                        exit_time: datetime,
                        timeframe: str = 'M5') -> dict | None:
        """
        Close position on MT5, build result dict, log to csv_manager.
        Returns closed trade dict or None.
        """
        position = self.active_positions.get(position_id)
        if position is None:
            return None

        symbol    = config.get('trading', 'symbol')
        ticket    = position.get('mt5_ticket')
        direction = position['direction']
        size      = float(position['size'])

        # ── Send close order to MT5 ───────────────────────────────────
        if ticket is not None:
            close_type = (mt5.ORDER_TYPE_SELL
                          if direction == 'long'
                          else mt5.ORDER_TYPE_BUY)
            tick  = mt5.symbol_info_tick(symbol)
            price = ((tick.bid if direction == 'long' else tick.ask)
                     if tick else exit_price)

            request = {
                'action'      : mt5.TRADE_ACTION_DEAL,
                'symbol'      : symbol,
                'volume'      : size,
                'type'        : close_type,
                'position'    : ticket,
                'price'       : price,
                'deviation'   : 20,
                'magic'       : 234000,
                'comment'     : replace_special(f'close:{exit_reason}'[:31]),
                'type_time'   : mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                exit_price = result.price
            else:
                code = result.retcode if result else 'None'
                logger.log_error(
                    f'close_position MT5 failed: retcode={code} — '
                    f'closing internally anyway')

        # ── PnL ───────────────────────────────────────────────────────
        pnl_points = (exit_price - position['entry_price']
                      if direction == 'long'
                      else position['entry_price'] - exit_price)

        result_dict = {
            'position_id'             : position_id,
            'direction'               : direction,
            'entry_price'             : position['entry_price'],
            'exit_price'              : exit_price,
            'entry_time'              : position['entry_time'],
            'exit_time'               : exit_time,
            'size'                    : size,
            'pnl_points'              : pnl_points,
            'outcome'                 : exit_reason,
            'bars_in_trade'           : position['bars_in_trade'],
            'max_favorable_excursion' : position['max_favorable_excursion'],
            'max_adverse_excursion'   : position['max_adverse_excursion'],
            'sl_updates_count'        : len(position['sl_updates']),
            'tp_updates_count'        : len(position['tp_updates']),
            'entry_p_tp'              : position.get('entry_p_tp'),
            'entry_edge'              : position.get('entry_edge'),
            'surface_id'              : position.get('surface_id'),
            'mu'                      : position.get('mu'),
        }

        self.closed_trades.append(result_dict)
        csv_manager.log_trade(timeframe, result_dict)
        logger.log_trade_exit(exit_time, exit_price, pnl_points, exit_reason)

        del self.active_positions[position_id]
        return result_dict

    # ── PER-BAR UPDATE ────────────────────────────────────────────────────────

    def update_position(self, position_id: str,
                         current_bar: dict,
                         atr_series: pd.Series,
                         timeframe: str = 'M5') -> dict | None:
        """
        Called every bar while a position is open.
        Updates MFE/MAE, applies trailing SL and ATR-based TP on schedule.
        Returns position dict (still open) or None if not found.
        """
        position = self.active_positions.get(position_id)
        if position is None:
            return None

        position['bars_in_trade'] += 1
        current_price = current_bar['close']

        position['highest_price'] = max(position['highest_price'],
                                         current_bar['high'])
        position['lowest_price']  = min(position['lowest_price'],
                                         current_bar['low'])

        if position['direction'] == 'long':
            mfe = position['highest_price'] - position['entry_price']
            mae = position['entry_price']   - position['lowest_price']
        else:
            mfe = position['entry_price']   - position['lowest_price']
            mae = position['highest_price'] - position['entry_price']

        position['max_favorable_excursion'] = max(
            position['max_favorable_excursion'], mfe)
        position['max_adverse_excursion'] = max(
            position['max_adverse_excursion'], mae)

        update_freq = config.get('position_management',
                                   'update_tp_sl_every_bars')

        if position['bars_in_trade'] % update_freq == 0:
            self._update_stop_loss(position, current_price, position_id)
            self._update_take_profit(position, current_bar,
                                      atr_series, position_id)

        return position

    def _update_stop_loss(self, position: dict,
                           current_price: float,
                           position_id: str):
        if not config.get('position_management', 'sl_trailing_enabled'):
            return

        entry_price  = position['entry_price']
        initial_risk = position['sl_distance_initial']
        trigger_rr   = config.get('position_management', 'sl_trail_trigger_rr')
        trail_pct    = config.get('position_management', 'sl_trail_distance_pct')

        if position['direction'] == 'long':
            unrealized = current_price - entry_price
        else:
            unrealized = entry_price - current_price

        if unrealized < initial_risk * trigger_rr:
            return

        if position['direction'] == 'long':
            new_stop = current_price - (unrealized * trail_pct)
        else:
            new_stop = current_price + (unrealized * trail_pct)

        self.modify_sl_mt5(position_id, new_stop)

    def _update_take_profit(self, position: dict,
                             current_bar: dict,
                             atr_series: pd.Series,
                             position_id: str):
        delay = config.get('position_management', 'tp_atr_delay')
        if len(atr_series) < delay:
            return

        delayed_atr   = atr_series.iloc[-delay]
        tp_multiplier = config.get('position_management', 'tp_atr_multiplier')
        entry_price   = position['entry_price']

        if position['direction'] == 'long':
            new_target = round(entry_price + delayed_atr * tp_multiplier, 2)
        else:
            new_target = round(entry_price - delayed_atr * tp_multiplier, 2)

        if new_target != position['current_target']:
            self.modify_tp_mt5(position_id, new_target)

    # ── EXIT CONDITIONS ───────────────────────────────────────────────────────

    def check_exit_conditions(self, position_id: str,
                               current_bar: dict
                               ) -> tuple:
        """
        Check high/low for intrabar SL/TP hits.
        Same open-proximity logic used in pde_backtest for the double-hit case.
        Returns (reason, exit_price) or (None, None).
        """
        position = self.active_positions.get(position_id)
        if position is None:
            return None, None

        high  = current_bar['high']
        low   = current_bar['low']
        open_ = current_bar['open']
        sl    = position['current_stop']
        tp    = position['current_target']

        if position['direction'] == 'long':
            if high >= tp and low <= sl:
                # Both — open closer to TP means TP hit first
                return (('TP', tp) if abs(open_ - tp) <= abs(open_ - sl)
                        else ('SL', sl))
            if high >= tp:
                return 'TP', tp
            if low <= sl:
                return 'SL', sl

        else:   # short
            if low <= tp and high >= sl:
                return (('TP', tp) if abs(open_ - tp) <= abs(open_ - sl)
                        else ('SL', sl))
            if low <= tp:
                return 'TP', tp
            if high >= sl:
                return 'SL', sl

        return None, None

    # ── PERIODIC STATS ────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """
        Return current performance stats from all closed trades this session.
        Call this at any time — from the main loop, on regime change, etc.
        """
        return compute_stats(self.closed_trades)

    def log_stats_on_regime_change(self, timeframe: str,
                                    surface_id: int,
                                    sigma_bar: float,
                                    sigma0: float,
                                    mu: float):
        """
        Called by strats.py every time the PDE surface is recomputed.
        Computes current stats and writes a snapshot to the session_stats CSV.
        """
        stats = self.get_stats()
        if not stats:
            return

        csv_manager.log_session_stats(timeframe, {
            'timestamp'    : datetime.now().isoformat(),
            'surface_id'   : surface_id,
            'sigma_bar'    : sigma_bar,
            'sigma0'       : sigma0,
            'mu'           : mu,
            'total_trades' : stats.get('total_trades'),
            'win_pct'      : stats.get('win_pct'),
            'total_pnl'    : stats.get('total_pnl'),
            'sharpe'       : stats.get('sharpe'),
            'max_drawdown' : stats.get('max_drawdown'),
            'calmar'       : stats.get('calmar'),
        })

        logger.log_system_event('regime_stats',
            f"[{timeframe}] surface={surface_id}  "
            f"trades={stats.get('total_trades')}  "
            f"win%={stats.get('win_pct', 0)*100:.1f}  "
            f"pnl={stats.get('total_pnl', 0):+.2f}  "
            f"sharpe={stats.get('sharpe', 0):.3f}  "
            f"maxDD={stats.get('max_drawdown', 0):.2f}")


position_manager = PositionManager()