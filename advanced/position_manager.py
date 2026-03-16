import numpy as np
import pandas as pd
from datetime import datetime
from config_loader import config

class PositionManager:
    def __init__(self):
        self.active_positions = {}
    
    def create_position(self, entry_decision, entry_time):

        if len(self.active_positions) > 0:
            return None
        
        position_id = f"{entry_decision['direction']}_{entry_time.strftime('%Y%m%d_%H%M%S')}"
        
        position = {
            'id': position_id,
            'direction': entry_decision['direction'],
            'signal': entry_decision['signal'],
            
            'entry_price': entry_decision['entry_price'],
            'entry_time': entry_time,
            'size': entry_decision['position_size'],
            
            'initial_stop': entry_decision['stop_price'],
            'current_stop': entry_decision['stop_price'],
            'initial_target': entry_decision['target_price'],
            'current_target': entry_decision['target_price'],
            
            'sl_distance_initial': entry_decision['sl_distance'],
            'tp_distance_initial': entry_decision['tp_distance'],
            
            'bars_in_trade': 0,
            
            'highest_price': entry_decision['entry_price'],
            'lowest_price': entry_decision['entry_price'],
            
            'max_favorable_excursion': 0,
            'max_adverse_excursion': 0,
            
            'sl_updates': [],
            'tp_updates': []
        }
        
        self.active_positions[position_id] = position
        return position
    
    def update_position(self, position_id, current_bar, atr_series):
        if position_id not in self.active_positions:
            return None
        
        position = self.active_positions[position_id]
        position['bars_in_trade'] += 1
        
        current_price = current_bar['close']
        
        position['highest_price'] = max(position['highest_price'], current_bar['high'])
        position['lowest_price'] = min(position['lowest_price'], current_bar['low'])
        
        if position['direction'] == 'long':
            mfe = position['highest_price'] - position['entry_price']
            mae = position['entry_price'] - position['lowest_price']
        else:
            mfe = position['entry_price'] - position['lowest_price']
            mae = position['highest_price'] - position['entry_price']
        
        position['max_favorable_excursion'] = max(position['max_favorable_excursion'], mfe)
        position['max_adverse_excursion'] = max(position['max_adverse_excursion'], mae)
        
        update_frequency = config.get('position_management', 'update_tp_sl_every_bars')
        
        if position['bars_in_trade'] % update_frequency == 0:
            self._update_stop_loss(position, current_price)
            self._update_take_profit(position, current_bar, atr_series)
        
        return position
    
    def _update_stop_loss(self, position, current_price):
        if not config.get('position_management', 'sl_trailing_enabled'):
            return
        
        current_stop = position['current_stop']
        entry_price = position['entry_price']
        initial_risk = position['sl_distance_initial']
        
        if position['direction'] == 'long':
            unrealized_pnl = current_price - entry_price
        else:
            unrealized_pnl = entry_price - current_price
        
        trigger_rr = config.get('position_management', 'sl_trail_trigger_rr')
        
        if unrealized_pnl < initial_risk * trigger_rr:
            return
        
        trail_pct = config.get('position_management', 'sl_trail_distance_pct')
        
        if position['direction'] == 'long':
            new_stop = current_price - (unrealized_pnl * trail_pct)
            
            if new_stop > current_stop:
                position['current_stop'] = round(new_stop, 2)
                position['sl_updates'].append({
                    'bar': position['bars_in_trade'],
                    'old_sl': current_stop,
                    'new_sl': new_stop,
                    'reason': 'Trailing (profit protection)'
                })
        else:
            new_stop = current_price + (unrealized_pnl * trail_pct)
            
            if new_stop < current_stop:
                position['current_stop'] = round(new_stop, 2)
                position['sl_updates'].append({
                    'bar': position['bars_in_trade'],
                    'old_sl': current_stop,
                    'new_sl': new_stop,
                    'reason': 'Trailing (profit protection)'
                })
    
    def _update_take_profit(self, position, current_bar, atr_series):
        delay = config.get('position_management', 'tp_atr_delay')
        
        if len(atr_series) < delay:
            return
        
        delayed_atr = atr_series.iloc[-delay]
        
        tp_multiplier = config.get('position_management', 'tp_atr_multiplier')
        
        entry_price = position['entry_price']
        
        if position['direction'] == 'long':
            new_target = entry_price + (delayed_atr * tp_multiplier)
        else:
            new_target = entry_price - (delayed_atr * tp_multiplier)
        
        new_target = round(new_target, 2)
        
        if new_target != position['current_target']:
            position['tp_updates'].append({
                'bar': position['bars_in_trade'],
                'old_tp': position['current_target'],
                'new_tp': new_target,
                'atr': delayed_atr
            })
            position['current_target'] = new_target
    
    def check_exit_conditions(self, position_id, current_bar):
        if position_id not in self.active_positions:
            return None, None
        
        position = self.active_positions[position_id]
        
        high = current_bar['high']
        low = current_bar['low']
        close = current_bar['close']
        
        if position['direction'] == 'long':
            if low <= position['current_stop']:
                return 'SL', position['current_stop']
            
            if high >= position['current_target']:
                return 'TP', position['current_target']
        
        else:
            if high >= position['current_stop']:
                return 'SL', position['current_stop']
            
            if low <= position['current_target']:
                return 'TP', position['current_target']
                
        return None, None
    
    def close_position(self, position_id, exit_price, exit_reason, exit_time):
        if position_id not in self.active_positions:
            return None
        
        position = self.active_positions[position_id]
        
        if position['direction'] == 'long':
            pnl_points = exit_price - position['entry_price']
        else:
            pnl_points = position['entry_price'] - exit_price
        
        contract_size = config.get('risk_management', 'contract_size')
        pnl_dollars = pnl_points * position['size'] * contract_size
        
        result = {
            'position_id': position_id,
            'direction': position['direction'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'entry_time': position['entry_time'],
            'exit_time': exit_time,
            'size': position['size'],
            'pnl_points': pnl_points,
            'pnl': pnl_dollars,
            'exit_reason': exit_reason,
            'bars_in_trade': position['bars_in_trade'],
            'max_favorable_excursion': position['max_favorable_excursion'],
            'max_adverse_excursion': position['max_adverse_excursion'],
            'sl_updates_count': len(position['sl_updates']),
            'tp_updates_count': len(position['tp_updates'])
        }
        
        del self.active_positions[position_id]
        
        return result
    
    def get_active_position(self):
        if len(self.active_positions) == 0:
            return None
        
        return list(self.active_positions.values())[0]

position_manager = PositionManager()
