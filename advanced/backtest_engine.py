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

class BacktestEngine:
    def __init__(self):
        self.trades = []
        self.equity_curve = []
    
    def run_backtest(self, df, timeframe='M5'):
        print(f"\n{'='*70}")
        print(f"BACKTESTING ON {timeframe} DATA")
        print(f"{'='*70}")
        print(f"Total bars: {len(df)}")
        print(f"Date range: {df['time'].iloc[0]} to {df['time'].iloc[-1]}")
        
        df = metrics_calculator.calculate_all_metrics(df, timeframe)
        
        risk_mgr = ProfessionalRiskManager()
        pos_mgr = PositionManager()
        
        starting_balance = risk_mgr.account_balance
        
        for i in range(50, len(df)):
            current_df = df.iloc[:i+1]
            
            vol_profile, vpoc, val, vah = metrics_calculator.calculate_volume_profile(
                current_df,
                lookback=min(500, len(current_df))
            )
            
            signal = signal_generator.generate_signal(current_df)
            
            latest_row = current_df.iloc[-1]
            
            active_pos = pos_mgr.get_active_position()
            
            if active_pos:
                atr_series = current_df['atr']
                pos_mgr.update_position(active_pos['id'], latest_row, atr_series)
                
                exit_reason, exit_price = pos_mgr.check_exit_conditions(
                    active_pos['id'],
                    latest_row
                )
                
                if exit_reason:
                    result = pos_mgr.close_position(
                        active_pos['id'],
                        exit_price,
                        exit_reason,
                        latest_row['time']
                    )
                    
                    self.trades.append(result)
                    risk_mgr.record_trade(result)
                    
                    self.equity_curve.append({
                        'timestamp': latest_row['time'],
                        'equity': risk_mgr.account_balance,
                        'pnl': result['pnl']
                    })
            
            if signal != 0 and active_pos is None:
                decision = risk_mgr.assess_risk(latest_row, vpoc, val, vah, signal)
                
                if decision.get('should_trade'):
                    position = pos_mgr.create_position(decision, latest_row['time'])
        
        final_balance = risk_mgr.account_balance
        total_return = ((final_balance - starting_balance) / starting_balance) * 100
        
        print(f"\n{'='*70}")
        print(f"BACKTEST RESULTS")
        print(f"{'='*70}")
        
        self._print_statistics(risk_mgr.get_statistics(), starting_balance, final_balance, total_return)
        
        self._generate_charts(timeframe)
        
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
        
        output_dir = Path(timeframe)
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_directory = config.get('output', 'charts_base_directory')
        filepath = Path(base_directory) / timeframe / f"backtest_charts_{timestamp}.png"
        
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"\n✅ Charts saved to: {filepath}")

if __name__ == "__main__":
    print("Backtest Engine - Load your OHLCV CSV and run backtest")
    print("Example:")
    print("  df = pd.read_csv('your_data.csv')")
    print("  df['time'] = pd.to_datetime(df['time'])")
    print("  engine = BacktestEngine()")
    print("  trades, equity = engine.run_backtest(df, 'M5')")
