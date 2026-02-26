import time
import pandas as pd
from datetime import datetime
from pathlib import Path

from config_loader import config
from logger import logger
from data_fetcher import data_fetcher
from metrics_calculator import metrics_calculator
from signal_generator import signal_generator
from risk_manager import risk_manager
from position_manager import position_manager
from csv_manager import csv_manager
from chart_generator import chart_generator

def print_terminal_report(timestamp, m5_row, decision, position, market_data):
    print("\n" + "="*70)
    print(f"MARKET UPDATE - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    m5_data = market_data['M5']
    h1_data = market_data.get('H1', {})
    h4_data = market_data.get('H4', {})
    
    m5_regime = m5_data.get('regime', 'unknown')
    h1_regime = h1_data.get('regime', 'unknown')
    h4_regime = h4_data.get('regime', 'unknown')
    
    print(f"TIMEFRAMES:")
    print(f"  M5: {m5_regime.upper()} | H1: {h1_regime.upper()} | H4: {h4_regime.upper()}")
    
    print(f"\nM5 LEVELS:")
    print(f"  VPOC: {m5_data.get('vpoc', 0):.2f} | VAH: {m5_data.get('vah', 0):.2f} | VAL: {m5_data.get('val', 0):.2f}")
    
    print(f"\nRISK ASSESSMENT:")
    print(f"  Risk Level: {decision.get('risk_level', 'N/A')} | Confidence: {decision.get('confidence', 0):.0f}/100")
    
    vrp = m5_row.get('vol_risk_premium', 0)
    rv = m5_row.get('realized_vol', 0)
    rel_vol = m5_row.get('relative_volume', 1)
    print(f"  VRP: {vrp:+.1f}% | Realized Vol: {rv:.2f}% | Rel Volume: {rel_vol:.1f}x")
    
    if 'signal_components' in decision:
        comp = decision['signal_components']
        print(f"\nSIGNAL COMPONENTS:")
        print(f"  VP Position: {comp.get('vp_position_score', 0):.1f} | Flow: {comp.get('order_flow_score', 0):.1f} | VWAP: {comp.get('vwap_relation_score', 0):.1f}")
        print(f"  MTF Multiplier: {comp.get('mtf_multiplier', 1.0):.2f}x | Final Score: {comp.get('filtered_score', 0):.1f}")
    
    if decision.get('should_trade'):
        print(f"\nSIGNAL:")
        print(f"  ✅ {decision['direction'].upper()} SETUP DETECTED")
        print(f"  Entry: {decision['entry_price']:.2f} | Stop: {decision['stop_price']:.2f} | Target: {decision['target_price']:.2f}")
        print(f"  Size: {decision['position_size']:.2f} lots | Risk: ${decision['dollar_risk']:.2f} | R:R: 1:{decision['risk_reward']:.1f}")
        print(f"  Strength: {decision.get('signal_strength', 0)*100:.0f}%")
    else:
        print(f"\nSIGNAL:")
        print(f"  ❌ NO TRADE - {decision.get('reason', 'No signal')}")
    
    print(f"\nPOSITION:")
    if position:
        unrealized = (m5_row['close'] - position['entry_price']) if position['direction'] == 'long' else (position['entry_price'] - m5_row['close'])
        unrealized_dollars = unrealized * position['size'] * config.get('risk_management', 'contract_size')
        
        print(f"  [{position['direction'].upper()}] Entry: {position['entry_price']:.2f} | Current: {m5_row['close']:.2f}")
        print(f"  P&L: ${unrealized_dollars:.2f} ({unrealized:.2f} pts)")
        print(f"  Stop: {position['current_stop']:.2f} | Target: {position['current_target']:.2f}")
        print(f"  Bars in trade: {position['bars_in_trade']}/{position['ttl_bars']}")
    else:
        print(f"  [NONE]")
    
    if decision.get('warnings'):
        print(f"\nWARNINGS:")
        for warning in decision['warnings']:
            print(f"  {warning}")
    
    print("="*70)

def main():
    print("="*70)
    print("MULTI-TIMEFRAME TRADING SYSTEM")
    print("="*70)
    
    if not data_fetcher.connect():
        print("Failed to connect to MT5")
        return
    
    timeframes_to_track = ['M5', 'H1', 'H4']
    update_interval = config.get('trading', 'update_interval_seconds')
    max_iterations = config.get('trading', 'max_iterations')
    
    print(f"\nConfiguration:")
    print(f"  Timeframes: {', '.join(timeframes_to_track)}")
    print(f"  Update Interval: {update_interval}s")
    print(f"  Max Iterations: {max_iterations}")
    
    market_data = {}
    for tf in timeframes_to_track:
        market_data[tf] = {
            'df': None,
            'vpoc': None,
            'val': None,
            'vah': None,
            'regime': None,
            'last_bar_time': None
        }
    
    iteration = 0
    
    try:
        while iteration < max_iterations:
            iteration += 1
            timestamp = datetime.now()
            
            logger.log_system_event('iteration_start', f"Iteration {iteration}")
            
            for tf in timeframes_to_track:
                df, updated = data_fetcher.update_df(tf)
                
                if df is None:
                    continue
                
                if not updated:
                    continue
                
                df = metrics_calculator.calculate_all_metrics(df, tf)
                
                vol_profile, vpoc, val, vah = metrics_calculator.calculate_volume_profile(
                    df,
                    lookback=config.get('volume_profile', 'lookback_bars')
                )
                
                print(tf,vpoc, val, vah)

                latest = df.iloc[-1]
                er = latest.get('efficiency_ratio', 0.5)
                regime = 'trending' if er > 0.6 else 'ranging' if er < 0.3 else 'transitional'
                
                market_data[tf] = {
                    'df': df,
                    'vpoc': vpoc,
                    'val': val,
                    'vah': vah,
                    'regime': regime,
                    'last_bar_time': latest['time']
                }
                
                signal_for_csv = 0
                if tf == 'M5':
                    signal_for_csv = signal_generator.generate_signal(df)
                
                csv_manager.append_bar_data(tf, latest, vpoc, val, vah, regime, signal_for_csv)
                
                chart_generator.generate_chart(df, tf, vpoc, val, vah, regime)
                
                print(f"[{timestamp.strftime('%H:%M:%S')}] {tf} bar updated | Regime: {regime}")
            
            if market_data['M5']['df'] is None:
                print(f"[{timestamp.strftime('%H:%M:%S')}] No M5 data, waiting...")
                time.sleep(update_interval)
                continue
            
            signal, strength, components = signal_generator.generate_signal_mtf(market_data)
            print(f"Multi-timeframe signal: {signal}, strength: {strength}, components: {components}")
            
            m5_latest = market_data['M5']['df'].iloc[-1]
            
            # why is the risk manager only using M5? not all Timeframe?
            decision = risk_manager.assess_risk(
                m5_latest,
                market_data['M5']['vpoc'],
                market_data['M5']['val'],
                market_data['M5']['vah'],
                signal,
                strength,
                components
            )
            print(f"Risk decision Details: {decision}")
            logger.log_trade_decision(timestamp, decision)
            
            active_position = position_manager.get_active_position()
            
            if active_position:
                atr_series = market_data['M5']['df']['atr']
                position_manager.update_position(active_position['id'], m5_latest, atr_series)
                
                exit_reason, exit_price = position_manager.check_exit_conditions(
                    active_position['id'],
                    m5_latest
                )
                
                if exit_reason:
                    result = position_manager.close_position(
                        active_position['id'],
                        exit_price,
                        exit_reason,
                        timestamp
                    )
                    
                    logger.log_trade_exit(timestamp, exit_price, result['pnl'], exit_reason)
                    risk_manager.record_trade(result)
                    
                    active_position = None
            
            if decision.get('should_trade') and active_position is None:
                tp = decision['target_price']
                sl = decision['stop_price']
                
                logger.log_tp_sl_calculation(timestamp, tp, sl, tp, sl)
                
                position = position_manager.create_position(decision, timestamp)
                logger.log_trade_execution(
                    timestamp,
                    decision['direction'],
                    decision['entry_price'],
                    decision['position_size'],
                    sl, tp,
                    position['ttl_bars']
                )
            
            print_terminal_report(timestamp, m5_latest, decision, active_position, market_data)
            
            time.sleep(update_interval)
            
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        logger.log_system_event('shutdown', "User interrupted")
    
    finally:
        data_fetcher.disconnect()
        
        stats = risk_manager.get_statistics()
        print("\n" + "="*70)
        print("SESSION SUMMARY")
        print("="*70)
        print(f"Total Trades: {stats.get('total_trades', 0)}")
        print(f"Win Rate: {stats.get('win_rate', 0):.1%}")
        print(f"Profit Factor: {stats.get('profit_factor', 0):.2f}")
        print(f"Sharpe Ratio: {stats.get('sharpe_ratio', 0):.2f}")
        print(f"Max Drawdown: ${stats.get('max_drawdown', 0):.2f}")
        print(f"Total P&L: ${stats.get('total_pnl', 0):.2f}")
        print("="*70)

if __name__ == "__main__":
    main()