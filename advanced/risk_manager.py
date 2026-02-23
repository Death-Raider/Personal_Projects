import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from config_loader import config
from logger import logger

class ProfessionalRiskManager:
    def __init__(self):
        self.account_balance = config.get('risk_management', 'account_balance')
        self.daily_starting_balance = self.account_balance
        self.daily_start_date = datetime.now().date()
        
        self.trade_history = []
        self.var_cache = None
        self.var_last_calc = None
    
    def assess_risk(self, df_row, vpoc, val, vah, signal):
        if signal == 0:
            return self._no_trade_decision("No signal")
        
        if not self._check_daily_drawdown_limit():
            return self._no_trade_decision("Daily drawdown limit reached")
        
        volatility_risk = self._calculate_volatility_risk(df_row)
        liquidity_risk = self._calculate_liquidity_risk(df_row)
        trend_risk = self._calculate_trend_risk(df_row)
        volume_confidence = self._calculate_volume_confidence(df_row)
        
        risk_score = (
            volatility_risk * 0.30 +
            liquidity_risk * 0.25 +
            trend_risk * 0.25 +
            (100 - volume_confidence) * 0.20
        )
        
        confidence_score = 100 - risk_score
        
        risk_level = self._classify_risk_level(risk_score)
        
        if risk_level in ['EXTREME', 'VERY_HIGH']:
            return self._no_trade_decision(f"Risk too high: {risk_level}")
        
        sl_distance = self._calculate_sl_distance(df_row, vpoc, val, vah, volatility_risk)
        tp_distance = self._calculate_tp_distance(df_row, vpoc, val, vah, confidence_score)
        
        rr_ratio = tp_distance / sl_distance if sl_distance > 0 else 0
        
        if rr_ratio < config.get('signals', 'min_risk_reward'):
            return self._no_trade_decision(f"Poor R:R ratio: {rr_ratio:.2f}")
        
        base_size = self._calculate_base_position_size(sl_distance)
        
        if config.get('risk_management', 'use_volatility_scaling'):
            base_size = self._apply_volatility_scaling(base_size, df_row)
        
        if config.get('risk_management', 'use_kelly_criterion') and len(self.trade_history) > 20:
            base_size = self._apply_kelly_criterion(base_size)
        
        base_size = self._apply_risk_level_adjustment(base_size, risk_level)
        
        base_size = np.clip(
            base_size,
            config.get('risk_management', 'min_lot_size'),
            config.get('risk_management', 'max_lot_size')
        )
        
        var = self._calculate_var(df_row, base_size) if config.get('risk_management', 'calculate_var') else 0
        
        current_price = df_row['close']
        if signal == 1:
            entry_price = current_price
            stop_price = entry_price - sl_distance
            target_price = entry_price + tp_distance
        else:
            entry_price = current_price
            stop_price = entry_price + sl_distance
            target_price = entry_price - tp_distance
        
        dollar_risk = sl_distance * base_size * config.get('risk_management', 'contract_size')
        
        decision = {
            'should_trade': True,
            'signal': signal,
            'direction': 'long' if signal == 1 else 'short',
            
            'risk_level': risk_level,
            'risk_score': risk_score,
            'confidence': confidence_score,
            
            'volatility_risk': volatility_risk,
            'liquidity_risk': liquidity_risk,
            'trend_risk': trend_risk,
            'volume_confidence': volume_confidence,
            
            'entry_price': round(entry_price, 2),
            'stop_price': round(stop_price, 2),
            'target_price': round(target_price, 2),
            
            'sl_distance': round(sl_distance, 2),
            'tp_distance': round(tp_distance, 2),
            'risk_reward': round(rr_ratio, 2),
            
            'position_size': round(base_size, 2),
            'dollar_risk': round(dollar_risk, 2),
            'var': round(var, 2),
            
            'warnings': []
        }
        
        logger.log_risk_assessment(datetime.now(), decision)
        
        return decision
    
    def _no_trade_decision(self, reason):
        return {
            'should_trade': False,
            'reason': reason,
            'signal': 0,
            'risk_score': 100,
            'confidence': 0
        }
    
    def _check_daily_drawdown_limit(self):
        today = datetime.now().date()
        
        if today != self.daily_start_date:
            self.daily_starting_balance = self.account_balance
            self.daily_start_date = today
        
        current_dd = ((self.daily_starting_balance - self.account_balance) / self.daily_starting_balance) * 100
        
        dd_limit = config.get('risk_management', 'daily_drawdown_limit_pct')
        
        if current_dd >= dd_limit:
            logger.log_drawdown_warning(current_dd, dd_limit)
            return False
        
        return True
    
    def _calculate_volatility_risk(self, row):
        rv = row.get('realized_vol', 20)
        vrp = row.get('vol_risk_premium', 0)
        
        risk = 0
        
        if rv > 30:
            risk += 40
        elif rv > 20:
            risk += 30
        elif rv > 10:
            risk += 15
        else:
            risk += 5
        
        if abs(vrp) > 15:
            risk += 30
        elif abs(vrp) > 10:
            risk += 20
        elif abs(vrp) > 5:
            risk += 10
        
        return min(risk, 100)
    
    def _calculate_liquidity_risk(self, row):
        illiq = row.get('amihud_illiquidity', 0.5)
        spread = row.get('spread_proxy', 0.01)
        
        risk = 0
        
        if illiq > 1.0:
            risk += 40
        elif illiq > 0.5:
            risk += 25
        else:
            risk += 10
        
        if spread > 0.02:
            risk += 40
        elif spread > 0.01:
            risk += 25
        else:
            risk += 10
        
        return min(risk, 100)
    
    def _calculate_trend_risk(self, row):
        er = row.get('efficiency_ratio', 0.5)
        
        if 0.3 <= er <= 0.7:
            return 70
        elif er < 0.2:
            return 50
        else:
            return 20
    
    def _calculate_volume_confidence(self, row):
        rel_vol = row.get('relative_volume', 1.0)
        cum_delta = abs(row.get('cumulative_delta', 0))
        
        confidence = 0
        
        if rel_vol > 2.0:
            confidence += 50
        elif rel_vol > 1.5:
            confidence += 35
        elif rel_vol > 1.0:
            confidence += 25
        elif rel_vol > 0.5:
            confidence += 15
        else:
            confidence += 5
        
        if cum_delta > 10000:
            confidence += 40
        elif cum_delta > 5000:
            confidence += 30
        elif cum_delta > 2000:
            confidence += 20
        else:
            confidence += 10
        
        return min(confidence, 100)
    
    def _classify_risk_level(self, risk_score):
        if risk_score >= 80:
            return 'EXTREME'
        elif risk_score >= 65:
            return 'VERY_HIGH'
        elif risk_score >= 50:
            return 'HIGH'
        elif risk_score >= 35:
            return 'MODERATE'
        elif risk_score >= 20:
            return 'LOW'
        else:
            return 'VERY_LOW'
    
    def _calculate_sl_distance(self, row, vpoc, val, vah, vol_risk):
        atr = row.get('atr', row['close'] * 0.01)
        
        atr_multiplier = config.get('position_management', 'sl_initial_atr_multiplier')
        atr_stop = atr * atr_multiplier
        
        value_area_width = vah - val
        vp_stop = value_area_width * 0.3
        
        base_stop = max(atr_stop, vp_stop)
        
        vol_multiplier = 1.0 + (vol_risk / 200)
        adjusted_stop = base_stop * vol_multiplier
        
        min_stop = row['close'] * 0.001
        final_stop = max(adjusted_stop, min_stop)
        
        return final_stop
    
    def _calculate_tp_distance(self, row, vpoc, val, vah, confidence):
        value_area_width = vah - val
        base_target = value_area_width
        
        confidence_mult = 1.0 + (confidence / 100)
        
        er = row.get('efficiency_ratio', 0.5)
        if er > 0.7:
            er_mult = 2.0
        elif er > 0.5:
            er_mult = 1.5
        else:
            er_mult = 1.0
        
        adjusted_target = base_target * confidence_mult * er_mult
        
        return adjusted_target
    
    def _calculate_base_position_size(self, sl_distance):
        base_risk_pct = config.get('risk_management', 'base_risk_per_trade_pct')
        base_dollar_risk = self.account_balance * (base_risk_pct / 100)
        
        contract_size = config.get('risk_management', 'contract_size')
        
        size = base_dollar_risk / (sl_distance * contract_size)
        
        return size
    
    def _apply_volatility_scaling(self, base_size, row):
        vol_target = config.get('risk_management', 'vol_target')
        current_vol = row.get('realized_vol', vol_target)
        
        vol_scalar = vol_target / max(current_vol, 1)
        vol_scalar = np.clip(vol_scalar, 0.5, 2.0)
        
        return base_size * vol_scalar
    
    def _apply_kelly_criterion(self, base_size):
        if len(self.trade_history) < 20:
            return base_size
        
        recent_trades = self.trade_history[-50:]
        
        wins = [t for t in recent_trades if t['pnl'] > 0]
        losses = [t for t in recent_trades if t['pnl'] < 0]
        
        if len(losses) == 0:
            return base_size
        
        win_rate = len(wins) / len(recent_trades)
        avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
        avg_loss = abs(np.mean([t['pnl'] for t in losses])) if losses else 1
        
        win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 1
        
        kelly_pct = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        kelly_pct = max(kelly_pct, 0)
        
        kelly_fraction = config.get('risk_management', 'kelly_fraction')
        fractional_kelly = kelly_pct * kelly_fraction
        
        kelly_size = self.account_balance * fractional_kelly / 100
        kelly_lots = kelly_size / (config.get('risk_management', 'contract_size') * 100)
        
        return min(base_size, kelly_lots)
    
    def _apply_risk_level_adjustment(self, base_size, risk_level):
        multipliers = {
            'VERY_LOW': 1.0,
            'LOW': 0.9,
            'MODERATE': 0.7,
            'HIGH': 0.5,
            'VERY_HIGH': 0.3,
            'EXTREME': 0.0
        }
        
        return base_size * multipliers.get(risk_level, 0.5)
    
    def _calculate_var(self, row, position_size):
        confidence = config.get('risk_management', 'var_confidence')
        horizon = config.get('risk_management', 'var_horizon_days')
        
        volatility_daily = row.get('realized_vol', 20) / 100 / np.sqrt(252)
        
        z_score = {0.90: 1.28, 0.95: 1.645, 0.99: 2.33}.get(confidence, 1.645)
        
        position_value = row['close'] * position_size * config.get('risk_management', 'contract_size')
        
        var = position_value * volatility_daily * z_score * np.sqrt(horizon)
        
        return var
    
    def record_trade(self, trade_result):
        self.trade_history.append(trade_result)
        self.account_balance += trade_result['pnl']
    
    def get_statistics(self):
        if len(self.trade_history) == 0:
            return {}
        
        total_trades = len(self.trade_history)
        wins = [t for t in self.trade_history if t['pnl'] > 0]
        losses = [t for t in self.trade_history if t['pnl'] <= 0]
        
        win_rate = len(wins) / total_trades
        
        total_pnl = sum(t['pnl'] for t in self.trade_history)
        gross_profit = sum(t['pnl'] for t in wins) if wins else 0
        gross_loss = abs(sum(t['pnl'] for t in losses)) if losses else 1
        
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        returns = [t['pnl'] / self.account_balance * 100 for t in self.trade_history]
        sharpe = (np.mean(returns) / np.std(returns) * np.sqrt(252)) if len(returns) > 1 else 0
        
        equity_curve = np.cumsum([t['pnl'] for t in self.trade_history])
        running_max = np.maximum.accumulate(equity_curve)
        drawdown = running_max - equity_curve
        max_drawdown = np.max(drawdown)
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'total_pnl': total_pnl
        }

risk_manager = ProfessionalRiskManager()
