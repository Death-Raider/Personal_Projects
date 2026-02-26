import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pathlib import Path
from datetime import datetime
from config_loader import config

class TradeVisualizer:
    def __init__(self):
        self.colors = {
            'win': '#26a69a',
            'loss': '#ef5350',
            'entry_long': 'green',
            'entry_short': 'red',
            'exit_tp': 'lime',
            'exit_sl': 'orange',
            'exit_ttl': 'yellow'
        }
    
    def plot_trades_on_chart(self, ohlc_df, trades_list, timeframe='M5', save_path=None):
        """
        Plot OHLC candlesticks with trade entry/exit markers
        
        Args:
            ohlc_df: DataFrame with ['time', 'open', 'high', 'low', 'close', 'tick_volume']
            trades_list: List of trade dictionaries from backtest
            timeframe: Timeframe name for title
            save_path: Path to save PNG (optional)
        """
        
        trades_df = pd.DataFrame(trades_list)
        
        if 'time' not in ohlc_df.columns:
            print("Error: OHLC dataframe must have 'time' column")
            return
        
        ohlc_df = ohlc_df.copy()
        ohlc_df['time'] = pd.to_datetime(ohlc_df['time'])
        trades_df['entry_time'] = pd.to_datetime(trades_df['entry_time'])
        trades_df['exit_time'] = pd.to_datetime(trades_df['exit_time'])
        
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(4, 1, hspace=0.3, height_ratios=[3, 1, 1, 1])
        
        ax_price = fig.add_subplot(gs[0])
        ax_equity = fig.add_subplot(gs[1])
        ax_drawdown = fig.add_subplot(gs[2])
        ax_stats = fig.add_subplot(gs[3])
        
        self._plot_candlesticks(ax_price, ohlc_df)
        
        self._plot_trade_markers(ax_price, ohlc_df, trades_df)
        
        self._plot_equity_curve(ax_equity, trades_df)
        
        self._plot_drawdown(ax_drawdown, trades_df)
        
        self._plot_statistics_table(ax_stats, trades_df)
        
        ax_price.set_title(f'Backtest Results - {timeframe} ({len(trades_df)} trades)', 
                          fontsize=16, fontweight='bold', pad=20)
        ax_price.set_ylabel('Price', fontsize=12, fontweight='bold')
        ax_price.grid(True, alpha=0.3, linestyle='--')
        ax_price.legend(loc='upper left', fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            output_path = Path(save_path)
            output_path.parent.mkdir(exist_ok=True, parents=True)
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"✅ Chart saved to: {output_path}")
        
        return fig
    
    def _plot_candlesticks(self, ax, df):
        """Plot OHLC candlesticks"""
        df = df.reset_index(drop=True)
        
        width = 0.6
        
        for idx, row in df.iterrows():
            x = idx
            
            ax.plot([x, x], [row['low'], row['high']], 
                   color='black', linewidth=0.8, alpha=0.6)
            
            if row['close'] >= row['open']:
                color = self.colors['win']
                lower = row['open']
                height = row['close'] - row['open']
            else:
                color = self.colors['loss']
                lower = row['close']
                height = row['open'] - row['close']
            
            if height < 0.01:
                height = 0.01
            
            rect = Rectangle((x - width/2, lower), width, height,
                           facecolor=color, edgecolor='black',
                           linewidth=0.5, alpha=0.8)
            ax.add_patch(rect)
    
    def _plot_trade_markers(self, ax, ohlc_df, trades_df):
        """Plot entry and exit markers on chart"""
        
        time_to_index = {time: idx for idx, time in enumerate(ohlc_df['time'])}
        
        entry_long_plotted = False
        entry_short_plotted = False
        exit_tp_plotted = False
        exit_sl_plotted = False
        exit_ttl_plotted = False
        
        for _, trade in trades_df.iterrows():
            entry_idx = time_to_index.get(trade['entry_time'])
            exit_idx = time_to_index.get(trade['exit_time'])
            
            if entry_idx is None or exit_idx is None:
                continue
            
            is_win = trade['pnl'] > 0
            direction = trade['direction']
            exit_reason = trade['exit_reason']
            
            if direction == 'long':
                entry_marker = '^'
                entry_color = self.colors['entry_long']
                entry_label = 'Long Entry' if not entry_long_plotted else ''
                entry_long_plotted = True
            else:
                entry_marker = 'v'
                entry_color = self.colors['entry_short']
                entry_label = 'Short Entry' if not entry_short_plotted else ''
                entry_short_plotted = True
            
            ax.scatter(entry_idx, trade['entry_price'], 
                      marker=entry_marker, s=200, 
                      color=entry_color, edgecolors='black', 
                      linewidth=2, zorder=10, label=entry_label)
            
            if exit_reason == 'TP':
                exit_color = self.colors['exit_tp']
                exit_label = 'TP Exit' if not exit_tp_plotted else ''
                exit_tp_plotted = True
            elif exit_reason == 'SL':
                exit_color = self.colors['exit_sl']
                exit_label = 'SL Exit' if not exit_sl_plotted else ''
                exit_sl_plotted = True
            else:
                exit_color = self.colors['exit_ttl']
                exit_label = 'TTL Exit' if not exit_ttl_plotted else ''
                exit_ttl_plotted = True
            
            ax.scatter(exit_idx, trade['exit_price'],
                      marker='X', s=250,
                      color=exit_color, edgecolors='black',
                      linewidth=2, zorder=10, label=exit_label)
            
            line_color = self.colors['win'] if is_win else self.colors['loss']
            ax.plot([entry_idx, exit_idx], 
                   [trade['entry_price'], trade['exit_price']],
                   linestyle='--', linewidth=1.5, 
                   color=line_color, alpha=0.6, zorder=5)
            
            mid_idx = (entry_idx + exit_idx) / 2
            mid_price = (trade['entry_price'] + trade['exit_price']) / 2
            
            pnl_text = f"${trade['pnl']:.1f}"
            ax.annotate(pnl_text, xy=(mid_idx, mid_price),
                       xytext=(0, 15), textcoords='offset points',
                       fontsize=8, fontweight='bold',
                       color='darkgreen' if is_win else 'darkred',
                       bbox=dict(boxstyle='round,pad=0.3', 
                               facecolor='white', 
                               edgecolor=line_color, 
                               alpha=0.8),
                       ha='center', zorder=15)
    
    def _plot_equity_curve(self, ax, trades_df):
        """Plot cumulative equity curve"""
        trades_df = trades_df.sort_values('entry_time').reset_index(drop=True)
        trades_df['cumulative_pnl'] = trades_df['pnl'].cumsum()
        
        ax.plot(trades_df.index, trades_df['cumulative_pnl'], 
               linewidth=2, color='blue', label='Equity')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.3)
        
        wins = trades_df[trades_df['pnl'] > 0]
        losses = trades_df[trades_df['pnl'] <= 0]
        
        ax.scatter(wins.index, wins['cumulative_pnl'], 
                  color=self.colors['win'], s=50, alpha=0.6, zorder=5)
        ax.scatter(losses.index, losses['cumulative_pnl'], 
                  color=self.colors['loss'], s=50, alpha=0.6, zorder=5)
        
        ax.set_ylabel('Cumulative P&L ($)', fontsize=11, fontweight='bold')
        ax.set_xlabel('Trade Number', fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='upper left', fontsize=9)
        
        final_pnl = trades_df['cumulative_pnl'].iloc[-1]
        color = 'green' if final_pnl > 0 else 'red'
        ax.text(0.98, 0.95, f'Final P&L: ${final_pnl:.2f}',
               transform=ax.transAxes, fontsize=11, fontweight='bold',
               verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor=color, alpha=0.3))
    
    def _plot_drawdown(self, ax, trades_df):
        """Plot drawdown from peak"""
        trades_df = trades_df.sort_values('entry_time').reset_index(drop=True)
        trades_df['cumulative_pnl'] = trades_df['pnl'].cumsum()
        
        running_max = trades_df['cumulative_pnl'].cummax()
        drawdown = trades_df['cumulative_pnl'] - running_max
        
        ax.fill_between(trades_df.index, 0, drawdown, 
                       color=self.colors['loss'], alpha=0.3)
        ax.plot(trades_df.index, drawdown, 
               linewidth=2, color='darkred')
        
        ax.set_ylabel('Drawdown ($)', fontsize=11, fontweight='bold')
        ax.set_xlabel('Trade Number', fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        max_dd = drawdown.min()
        max_dd_idx = drawdown.idxmin()
        
        ax.scatter([max_dd_idx], [max_dd], color='red', s=100, 
                  zorder=10, marker='v')
        ax.text(0.98, 0.05, f'Max DD: ${max_dd:.2f}',
               transform=ax.transAxes, fontsize=11, fontweight='bold',
               verticalalignment='bottom', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='red', alpha=0.3))
    
    def _plot_statistics_table(self, ax, trades_df):
        """Plot statistics as table"""
        ax.axis('off')
        
        total_trades = len(trades_df)
        wins = trades_df[trades_df['pnl'] > 0]
        losses = trades_df[trades_df['pnl'] <= 0]
        
        win_rate = len(wins) / total_trades * 100 if total_trades > 0 else 0
        
        total_pnl = trades_df['pnl'].sum()
        gross_profit = wins['pnl'].sum() if len(wins) > 0 else 0
        gross_loss = abs(losses['pnl'].sum()) if len(losses) > 0 else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        avg_win = wins['pnl'].mean() if len(wins) > 0 else 0
        avg_loss = losses['pnl'].mean() if len(losses) > 0 else 0
        avg_rr = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        exit_reasons = trades_df['exit_reason'].value_counts()
        
        stats_text = f"""
        TRADE STATISTICS
        
        Total Trades: {total_trades}
        Wins: {len(wins)} ({win_rate:.1f}%)
        Losses: {len(losses)} ({100-win_rate:.1f}%)
        
        Total P&L: ${total_pnl:.2f}
        Profit Factor: {profit_factor:.2f}
        Avg R:R: 1:{avg_rr:.2f}
        
        Avg Win: ${avg_win:.2f}
        Avg Loss: ${avg_loss:.2f}
        
        Exit Reasons:
        TP: {exit_reasons.get('TP', 0)}
        SL: {exit_reasons.get('SL', 0)}
        TTL: {exit_reasons.get('TTL', 0)}
        """
        
        ax.text(0.05, 0.95, stats_text,
               transform=ax.transAxes,
               fontsize=11, verticalalignment='top',
               fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

def visualize_backtest(ohlc_df, trades_list, timeframe='M5'):
    """
    Main function to create backtest visualization
    
    Args:
        ohlc_df: DataFrame with OHLC data
        trades_list: List of trade dictionaries from backtest
        timeframe: Timeframe name
    
    Returns:
        matplotlib figure
    """
    visualizer = TradeVisualizer()
    base_directory = config.get('output', 'charts_base_directory')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_path = f"{base_directory}/{timeframe}/backtest_visualization_{timestamp}.png"
    
    fig = visualizer.plot_trades_on_chart(
        ohlc_df=ohlc_df,
        trades_list=trades_list,
        timeframe=timeframe,
        save_path=save_path
    )
    
    return fig

if __name__ == "__main__":
    print("Trade Visualizer")
    print("\nUsage:")
    print("  from trade_visualizer import visualize_backtest")
    print("  fig = visualize_backtest(ohlc_df, trades_list, 'M5')")
    print("  plt.show()")
