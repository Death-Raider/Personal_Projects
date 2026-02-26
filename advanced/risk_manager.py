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
    
    def assess_risk(self, df_row, vpoc, val, vah, signal, signal_strength=1.0, signal_components=None):
        if signal == 0:
            return self._no_trade_decision("No signal")
        
        if not self._check_daily_drawdown_limit():
            return self._no_trade_decision("Daily drawdown limit reached")
        
        volatility_risk = self._calculate_volatility_risk(df_row)
        liquidity_risk = self._calculate_liquidity_risk(df_row)
        trend_risk = self._calculate_trend_risk(df_row)
        volume_confidence = self._calculate_volume_confidence(df_row)
        
        vp_position_score = self._calculate_vp_position_score(df_row, vpoc, val, vah)
        order_flow_score = self._calculate_order_flow_score(df_row)
        vwap_relation_score = self._calculate_vwap_relation_score(df_row)
        
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
        
        position_size = 0.01
        
        var = self._calculate_var(df_row, position_size) if config.get('risk_management', 'calculate_var') else 0
        
        current_price = df_row['close']
        if signal == 1:
            entry_price = current_price
            stop_price = entry_price - sl_distance
            target_price = entry_price + tp_distance
        else:
            entry_price = current_price
            stop_price = entry_price + sl_distance
            target_price = entry_price - tp_distance
        
        dollar_risk = sl_distance * position_size * config.get('risk_management', 'contract_size')
        
        decision = {
            'should_trade': True,
            'signal': signal,
            'signal_strength': signal_strength,
            'direction': 'long' if signal == 1 else 'short',
            
            'risk_level': risk_level,
            'risk_score': risk_score,
            'confidence': confidence_score,
            
            'volatility_risk': volatility_risk,
            'liquidity_risk': liquidity_risk,
            'trend_risk': trend_risk,
            'volume_confidence': volume_confidence,
            
            'vp_position_score': vp_position_score,
            'order_flow_score': order_flow_score,
            'vwap_relation_score': vwap_relation_score,
            
            'entry_price': round(entry_price, 2),
            'stop_price': round(stop_price, 2),
            'target_price': round(target_price, 2),
            
            'sl_distance': round(sl_distance, 2),
            'tp_distance': round(tp_distance, 2),
            'risk_reward': round(rr_ratio, 2),
            
            'position_size': position_size,
            'dollar_risk': round(dollar_risk, 2),
            'var': round(var, 2),
            
            'warnings': []
        }
        
        if signal_components:
            decision['signal_components'] = signal_components
        
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
            # logger.log_drawdown_warning(current_dd, dd_limit)
            return False
        
        return True
    
    def _calculate_vp_position_score(self, row, vpoc, val, vah):
        price = row['close']
        cum_delta = row.get('cumulative_delta', 0)
        rel_vol = row.get('relative_volume', 1.0)
        
        va_width = vah - val
        if va_width == 0:
            return 0
        
        distance_from_vpoc = (price - vpoc) / va_width
        
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
            score = distance_from_vpoc * 40
        
        return score
    
    def _calculate_order_flow_score(self, row):
        cum_delta = row.get('cumulative_delta', 0)
        vol_delta = row.get('volume_delta', 0)
        rel_vol = row.get('relative_volume', 1.0)
        
        score = 0
        
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
        
        score = 0
        
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