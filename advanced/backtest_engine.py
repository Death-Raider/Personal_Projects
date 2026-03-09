import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

from metrics_calculator import metrics_calculator
from signal_generator import signal_generator
from risk_manager import ProfessionalRiskManager
from position_manager import PositionManager
from config_loader import config
from trade_visualizer import TradeVisualizer

class BacktestEngine:
    def __init__(self):
        self.trades = []
        self.equity_curve = []
    
    def run_backtest(self, df, timeframe='M5', use_mtf=False, h1_df=None, h4_df=None):
        print(f"\n{'='*70}")
        print(f"BACKTESTING ON {timeframe} DATA")
        if use_mtf:
            print(f"Mode: MULTI-TIMEFRAME (M5 + H1 + H4)")
        else:
            print(f"Mode: SINGLE TIMEFRAME")
        print(f"{'='*70}")
        print(f"Total bars: {len(df)}")
        print(f"Date range: {df['time'].iloc[0]} to {df['time'].iloc[-1]}")
        
        df = metrics_calculator.calculate_all_metrics(df, timeframe)
        
        if use_mtf:
            if h1_df is not None:
                print(f"H1 bars: {len(h1_df)}")
                h1_df = metrics_calculator.calculate_all_metrics(h1_df, 'H1')
            if h4_df is not None:
                print(f"H4 bars: {len(h4_df)}")
                h4_df = metrics_calculator.calculate_all_metrics(h4_df, 'H4')
        
        risk_mgr = ProfessionalRiskManager()
        pos_mgr = PositionManager()
        
        starting_balance = risk_mgr.account_balance
        
        print(f"\nRunning backtest...")
        
        for i in range(50, len(df)):
            if i % 100 == 0:
                print(f"  Progress: {i}/{len(df)} bars processed...")
            
            current_df = df.iloc[:i+1]
            
            vol_profile, vpoc, val, vah = metrics_calculator.calculate_volume_profile(
                current_df,
                lookback=min(500, len(current_df))
            )
            
            latest_row = current_df.iloc[-1]
            
            if use_mtf and h1_df is not None and h4_df is not None:
                current_time = latest_row['time']
                
                h1_idx = (h1_df['time'] <= current_time).sum() - 1
                h4_idx = (h4_df['time'] <= current_time).sum() - 1
                
                if h1_idx >= 50 and h4_idx >= 50:
                    h1_current = h1_df.iloc[:h1_idx+1]
                    h4_current = h4_df.iloc[:h4_idx+1]
                    
                    _, h1_vpoc, h1_val, h1_vah = metrics_calculator.calculate_volume_profile(
                        h1_current, lookback=min(200, len(h1_current))
                    )
                    _, h4_vpoc, h4_val, h4_vah = metrics_calculator.calculate_volume_profile(
                        h4_current, lookback=min(100, len(h4_current))
                    )
                    
                    h1_latest = h1_current.iloc[-1]
                    h4_latest = h4_current.iloc[-1]
                    
                    h1_er = h1_latest.get('efficiency_ratio', 0.5)
                    h4_er = h4_latest.get('efficiency_ratio', 0.5)
                    
                    h1_regime = 'trending' if h1_er > 0.6 else 'ranging' if h1_er < 0.3 else 'transitional'
                    h4_regime = 'trending' if h4_er > 0.6 else 'ranging' if h4_er < 0.3 else 'transitional'
                    
                    m5_er = latest_row.get('efficiency_ratio', 0.5)
                    m5_regime = 'trending' if m5_er > 0.6 else 'ranging' if m5_er < 0.3 else 'transitional'
                    
                    market_data = {
                        'M5': {
                            'df': current_df,
                            'vpoc': vpoc,
                            'val': val,
                            'vah': vah,
                            'regime': m5_regime
                        },
                        'H1': {
                            'df': h1_current,
                            'vpoc': h1_vpoc,
                            'val': h1_val,
                            'vah': h1_vah,
                            'regime': h1_regime
                        },
                        'H4': {
                            'df': h4_current,
                            'vpoc': h4_vpoc,
                            'val': h4_val,
                            'vah': h4_vah,
                            'regime': h4_regime
                        }
                    }
                    # print(market_data)
                    
                    signal, strength, components = signal_generator.generate_signal_mtf(market_data)
                    # print(signal, strength, components)
                else:
                    signal = signal_generator.generate_signal(current_df)
                    strength = 1.0
                    components = {}
            else:
                signal = signal_generator.generate_signal(current_df)
                strength = 1.0
                components = {}
            
            active_pos = pos_mgr.get_active_position()
            
            if active_pos:
                atr_series = current_df['atr']
                pos_mgr.update_position(active_pos['id'], latest_row, atr_series)
                
                exit_reason, exit_price = pos_mgr.check_exit_conditions(
                    active_pos['id'],
                    latest_row
                )
                
                if exit_reason:
                    comp = active_pos.get('components', {})
                    stren = active_pos.get('strength', 1.0)
                    result = pos_mgr.close_position(
                        active_pos['id'],
                        exit_price,
                        exit_reason,
                        latest_row['time']
                    )
                    result['components'] = comp
                    result['strength'] = stren
                    self.trades.append(result)
                    risk_mgr.record_trade(result)
                    
                    self.equity_curve.append({
                        'timestamp': latest_row['time'],
                        'equity': risk_mgr.account_balance,
                        'pnl': result['pnl']
                    })
            
            if signal != 0 and active_pos is None:
                decision = risk_mgr.assess_risk(
                    latest_row, vpoc, val, vah, signal, strength, components
                )
                # print(decision)
                if decision.get('should_trade'):
                    position = pos_mgr.create_position(decision, latest_row['time'])
                    pos_mgr.active_positions[position['id']]['strength'] = strength
                    pos_mgr.active_positions[position['id']]['components'] = components
        
        print(f"  Completed: {len(df)} bars processed")
        
        final_balance = risk_mgr.account_balance
        total_return = ((final_balance - starting_balance) / starting_balance) * 100
        
        print(f"\n{'='*70}")
        print(f"BACKTEST RESULTS")
        print(f"{'='*70}")
        
        self._print_statistics(risk_mgr.get_statistics(), starting_balance, final_balance, total_return)
        
        self._generate_charts(timeframe)
        
        self._generate_trade_visualization(df, timeframe)
        
        return self.trades, self.equity_curve
    
    def _print_statistics(self, stats, starting, ending, return_pct):
        print(f"\nPERFORMANCE:")
        print(f"  Starting Balance: ${starting:,.2f}")
        print(f"  Ending Balance: ${ending:,.2f}")
        print(f"  Total Return: {return_pct:+.2f}%")
        print(f"  Total P&L: ${stats.get('total_pnl', 0):,.2f}")
        
        print(f"\nTRADE STATISTICS:")
        print(f"  Total Trades: {stats.get('total_trades', 0)}")
        print(f"  Win Rate: {stats.get('win_rate', 0):.1%}")
        print(f"  Profit Factor: {stats.get('profit_factor', 0):.2f}")
        
        print(f"\nRISK METRICS:")
        print(f"  Sharpe Ratio: {stats.get('sharpe_ratio', 0):.2f}")
        print(f"  Max Drawdown: ${stats.get('max_drawdown', 0):,.2f}")
        
        if len(self.trades) > 0:
            wins = [t for t in self.trades if t['pnl'] > 0]
            losses = [t for t in self.trades if t['pnl'] <= 0]
            
            avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
            avg_loss = np.mean([t['pnl'] for t in losses]) if losses else 0
            avg_rr = abs(avg_win / avg_loss) if avg_loss != 0 else 0
            
            print(f"  Average R:R: 1:{avg_rr:.2f}")
            
            if wins:
                print(f"  Avg Win: ${avg_win:.2f}")
            if losses:
                print(f"  Avg Loss: ${avg_loss:.2f}")
    
    def _generate_charts(self, timeframe):
        if len(self.equity_curve) == 0:
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        equity_df = pd.DataFrame(self.equity_curve)
        
        ax1.plot(equity_df.index, equity_df['equity'], linewidth=2, color='blue')
        ax1.set_title('Equity Curve', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Trade Number')
        ax1.set_ylabel('Account Balance ($)')
        ax1.grid(True, alpha=0.3)
        
        running_max = equity_df['equity'].cummax()
        drawdown = running_max - equity_df['equity']
        
        ax2.fill_between(equity_df.index, 0, -drawdown, color='red', alpha=0.3)
        ax2.plot(equity_df.index, -drawdown, linewidth=2, color='darkred')
        ax2.set_title('Drawdown', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Trade Number')
        ax2.set_ylabel('Drawdown ($)')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        base_directory = config.get('output', 'charts_base_directory')
        output_dir = Path(base_directory) / timeframe
        output_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = output_dir / f"backtest_charts_{timestamp}.png"
        
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"\n✅ Equity/Drawdown charts saved to: {filepath}")
    
    def _generate_trade_visualization(self, df, timeframe):
        if len(self.trades) == 0:
            return
        
        print(f"\n📊 Generating trade visualization...")
        
        visualizer = TradeVisualizer()
        
        base_directory = config.get('output', 'charts_base_directory')
        output_dir = Path(base_directory) / timeframe
        output_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = output_dir / f'trades_visualization_{timestamp}.png'
        
        visualizer.plot_trades_on_chart(
            ohlc_df=df,
            trades_list=self.trades,
            timeframe=timeframe,
            save_path=str(filepath)
        )

if __name__ == "__main__":
    print("=" * 70)
    print("BACKTEST ENGINE - Multi-Timeframe Capable")
    print("=" * 70)
    
    print("\n📊 SINGLE TIMEFRAME MODE:")
    print("-" * 70)
    print("  df = pd.read_csv('m5_data.csv')")
    print("  df['time'] = pd.to_datetime(df['time'])")
    print("  ")
    print("  engine = BacktestEngine()")
    print("  trades, equity = engine.run_backtest(df, 'M5')")
    
    print("\n📊 MULTI-TIMEFRAME MODE:")
    print("-" * 70)
    print("  m5_df = pd.read_csv('m5_data.csv')")
    print("  h1_df = pd.read_csv('h1_data.csv')")
    print("  h4_df = pd.read_csv('h4_data.csv')")
    print("  ")
    print("  # Convert timestamps")
    print("  for df in [m5_df, h1_df, h4_df]:")
    print("      df['time'] = pd.to_datetime(df['time'])")
    print("  ")
    print("  engine = BacktestEngine()")
    print("  trades, equity = engine.run_backtest(")
    print("      m5_df, 'M5',")
    print("      use_mtf=True,")
    print("      h1_df=h1_df,")
    print("      h4_df=h4_df")
    print("  )")
    
    print("\n💡 BENEFITS OF MULTI-TIMEFRAME:")
    print("-" * 70)
    print("  • Higher timeframe confluence (H1/H4 bias)")
    print("  • Better signal filtering (2x multiplier when aligned)")
    print("  • Reduced false signals (0.5x penalty when conflicting)")
    print("  • More robust trade decisions")
    
    print("\n" + "=" * 70)