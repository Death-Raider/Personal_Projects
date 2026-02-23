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

def print_terminal_report(timestamp, df_row, decision, position, vpoc, val, vah):
    print("\n" + "="*70)
    print(f"MARKET UPDATE - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    timeframe = config.get('trading', 'active_timeframe')
    er = df_row.get('efficiency_ratio', 0)
    regime = "TRENDING" if er > 0.6 else "RANGING" if er < 0.3 else "TRANSITIONAL"
    
    print(f"Timeframe: {timeframe} | Regime: {regime} | ER: {er:.2f}")
    
    print(f"\nLEVELS:")
    print(f"  VPOC: {vpoc:.2f} | VAH: {vah:.2f} | VAL: {val:.2f}")
    
    print(f"\nRISK ASSESSMENT:")
    print(f"  Risk Level: {decision.get('risk_level', 'N/A')} | Confidence: {decision.get('confidence', 0):.0f}/100")
    
    vrp = df_row.get('vol_risk_premium', 0)
    rv = df_row.get('realized_vol', 0)
    rel_vol = df_row.get('relative_volume', 1)
    print(f"  VRP: {vrp:+.1f}% | Realized Vol: {rv:.2f}% | Rel Volume: {rel_vol:.1f}x")
    
    if decision.get('should_trade'):
        print(f"\nSIGNAL:")
        print(f"  ✅ {decision['direction'].upper()} SETUP DETECTED")
        print(f"  Entry: {decision['entry_price']:.2f} | Stop: {decision['stop_price']:.2f} | Target: {decision['target_price']:.2f}")
        print(f"  Size: {decision['position_size']:.2f} lots | Risk: ${decision['dollar_risk']:.2f} | R:R: 1:{decision['risk_reward']:.1f}")
    else:
        print(f"\nSIGNAL:")
        print(f"  ❌ NO TRADE - {decision.get('reason', 'No signal')}")
    
    print(f"\nPOSITION:")
    if position:
        unrealized = (df_row['close'] - position['entry_price']) if position['direction'] == 'long' else (position['entry_price'] - df_row['close'])
        unrealized_dollars = unrealized * position['size'] * config.get('risk_management', 'contract_size')
        
        print(f"  [{position['direction'].upper()}] Entry: {position['entry_price']:.2f} | Current: {df_row['close']:.2f}")
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

def save_to_csv(df_row, timeframe, decision):
    csv_dir = Path(config.get('output', 'csv_directory'))
    csv_path = csv_dir / f"Historical_Data_{timeframe}.csv"
    
    row_data = {
        'timestamp': df_row.get('time'),
        'open': df_row.get('open'),
        'high': df_row.get('high'),
        'low': df_row.get('low'),
        'close': df_row.get('close'),
        'tick_volume': df_row.get('tick_volume'),
        'vwap': df_row.get('vwap'),
        'volume_delta': df_row.get('volume_delta'),
        'cumulative_delta': df_row.get('cumulative_delta'),
        'relative_volume': df_row.get('relative_volume'),
        'realized_vol': df_row.get('realized_vol'),
        'implied_vol': df_row.get('implied_vol'),
        'vol_risk_premium': df_row.get('vol_risk_premium'),
        'efficiency_ratio': df_row.get('efficiency_ratio'),
        'signal': decision.get('signal', 0),
        'should_trade': decision.get('should_trade', False),
        'risk_level': decision.get('risk_level', ''),
        'confidence': decision.get('confidence', 0)
    }
    
    row_df = pd.DataFrame([row_data])
    
    if csv_path.exists():
        row_df.to_csv(csv_path, mode='a', header=False, index=False)
    else:
        row_df.to_csv(csv_path, mode='w', header=True, index=False)

def main():
    print("="*70)
    print("TRADING SYSTEM INTEGRATION")
    print("="*70)
    
    if not data_fetcher.connect():
        print("Failed to connect to MT5")
        return
    
    timeframe = config.get('trading', 'active_timeframe')
    update_interval = config.get('trading', 'update_interval_seconds')
    max_iterations = config.get('trading', 'max_iterations')
    
    print(f"\nConfiguration:")
    print(f"  Timeframe: {timeframe}")
    print(f"  Update Interval: {update_interval}s")
    print(f"  Max Iterations: {max_iterations}")
    
    iteration = 0
    
    try:
        while iteration < max_iterations:
            iteration += 1
            timestamp = datetime.now()
            
            logger.log_system_event('iteration_start', f"Iteration {iteration}")
            
            df, updated = data_fetcher.update_df(timeframe)
            
            if df is None:
                logger.log_error("No data available")
                time.sleep(update_interval)
                continue
            
            if not updated:
                print(f"[{timestamp.strftime('%H:%M:%S')}] No new bar, waiting...")
                time.sleep(update_interval)
                continue
            
            df = metrics_calculator.calculate_all_metrics(df, timeframe)
            
            vol_profile, vpoc, val, vah = metrics_calculator.calculate_volume_profile(
                df, 
                lookback=config.get('volume_profile', 'lookback_bars')
            )
            
            signal = signal_generator.generate_signal(df)
            df.loc[df.index[-1], 'signal'] = signal
            
            latest_row = df.iloc[-1]
            
            decision = risk_manager.assess_risk(latest_row, vpoc, val, vah, signal)
            
            logger.log_trade_decision(timestamp, decision)
            
            active_position = position_manager.get_active_position()
            
            if active_position:
                atr_series = df['atr']
                position_manager.update_position(active_position['id'], latest_row, atr_series)
                
                exit_reason, exit_price = position_manager.check_exit_conditions(
                    active_position['id'], 
                    latest_row
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
                
                # execute_trade(
                #     signal=decision['signal'],
                #     symbol=config.get('trading', 'symbol'),
                #     size=decision['position_size'],
                #     sl=sl,
                #     tp=tp
                # )
                
                position = position_manager.create_position(decision, timestamp)
                logger.log_trade_execution(
                    timestamp,
                    decision['direction'],
                    decision['entry_price'],
                    decision['position_size'],
                    sl, tp,
                    position['ttl_bars']
                )
            
            save_to_csv(latest_row, timeframe, decision)
            
            print_terminal_report(timestamp, latest_row, decision, active_position, vpoc, val, vah)
            
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
