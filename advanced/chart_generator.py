import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pandas as pd
from pathlib import Path
from config_loader import config
from signal_generator import signal_generator

class ChartGenerator:
    def __init__(self):
        self.base_dir = Path(config.get('output', 'charts_base_directory'))
        self.colors = {
            'up': '#26a69a',
            'down': '#ef5350',
            'vpoc': 'purple',
            'vwap': 'blue',
            'regime_trending': 'green',
            'regime_ranging': 'orange',
            'regime_transitional': 'yellow',
            'vp_score': '#FF6B6B',
            'flow_score': '#4ECDC4',
            'vwap_score': '#45B7D1',
            'final_score': '#FFA07A'
        }
    
    def generate_chart(self, df, timeframe, vpoc, val, vah, regime, signal=None):
        chart_path = self.base_dir / timeframe / 'current_chart.png'
        chart_path.parent.mkdir(parents=True, exist_ok=True)
        
        lookback = min(144, len(df))
        plot_df = df.tail(lookback).reset_index(drop=True)
        
        if len(plot_df) < 50:
            return
        
        metrics_list = []
        for idx, row in plot_df.iterrows():
            metrics = signal_generator.calculate_metrics(row, vpoc, val, vah)
            metrics_list.append(metrics)
        
        metrics_df = pd.DataFrame(metrics_list)
        
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(4, 1, hspace=0.3, height_ratios=[3, 1, 1, 1])
        
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        ax3 = fig.add_subplot(gs[2])
        ax4 = fig.add_subplot(gs[3])
        
        self._plot_candlesticks(ax1, plot_df)
        self._plot_levels(ax1, vpoc, val, vah)
        self._plot_vwap(ax1, plot_df)
        self._add_regime_label(ax1, regime, timeframe)
        
        self._plot_volume(ax2, plot_df)
        
        self._plot_component_scores(ax3, metrics_df)
        
        self._plot_final_scores(ax4, metrics_df)
        
        ax1.set_title(f'{timeframe} Chart - Regime: {regime.upper()}', 
                     fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price', fontsize=11)
        ax1.grid(True, alpha=0.2, linestyle='--')
        ax1.legend(loc='upper left', fontsize=9)
        
        ax2.set_ylabel('Volume', fontsize=11)
        ax2.grid(True, alpha=0.2, linestyle='--')
        
        ax3.set_ylabel('Component Scores', fontsize=11)
        ax3.grid(True, alpha=0.2, linestyle='--')
        ax3.legend(loc='upper left', fontsize=8)
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.3)
        
        ax4.set_xlabel('Bar Index', fontsize=11)
        ax4.set_ylabel('Final Score', fontsize=11)
        ax4.grid(True, alpha=0.2, linestyle='--')
        ax4.legend(loc='upper left', fontsize=8)
        ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.3)
        
        min_threshold = config.get('signals', 'min_confidence_score')
        ax4.axhline(y=min_threshold, color='green', linestyle='--', linewidth=1, alpha=0.5, label='Buy Threshold')
        ax4.axhline(y=-min_threshold, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Sell Threshold')
        
        plt.tight_layout()
        plt.savefig(chart_path, dpi=120, bbox_inches='tight')
        plt.close()
    
    def _plot_candlesticks(self, ax, df):
        width = 0.6
        
        for idx, row in df.iterrows():
            x = idx
            
            ax.plot([x, x], [row['low'], row['high']], 
                   color='black', linewidth=0.8, alpha=0.6)
            
            if row['close'] >= row['open']:
                color = self.colors['up']
                lower = row['open']
                height = row['close'] - row['open']
            else:
                color = self.colors['down']
                lower = row['close']
                height = row['open'] - row['close']
            
            if height < 0.01:
                height = 0.01
            
            rect = Rectangle((x - width/2, lower), width, height,
                           facecolor=color, edgecolor='black',
                           linewidth=0.5, alpha=0.8)
            ax.add_patch(rect)
    
    def _plot_levels(self, ax, vpoc, val, vah):
        if vpoc is not None:
            ax.axhline(y=vpoc, color=self.colors['vpoc'], 
                      linestyle='--', linewidth=1.5, label='VPOC', alpha=0.8)
        
        if val is not None and vah is not None:
            ax.axhspan(val, vah, alpha=0.1, color=self.colors['vpoc'], 
                      label='Value Area')
            ax.axhline(y=val, color=self.colors['vpoc'], 
                      linestyle=':', linewidth=1, alpha=0.6)
            ax.axhline(y=vah, color=self.colors['vpoc'], 
                      linestyle=':', linewidth=1, alpha=0.6)
    
    def _plot_vwap(self, ax, df):
        if 'vwap' in df.columns:
            ax.plot(df.index, df['vwap'], color=self.colors['vwap'], 
                   linewidth=1.5, label='VWAP', alpha=0.7)
    
    def _add_regime_label(self, ax, regime, timeframe):
        if regime == 'trending':
            color = self.colors['regime_trending']
        elif regime == 'ranging':
            color = self.colors['regime_ranging']
        else:
            color = self.colors['regime_transitional']
        
        ax.text(0.02, 0.98, f'{timeframe} | {regime.upper()}',
               transform=ax.transAxes, fontsize=12, fontweight='bold',
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor=color, alpha=0.7))
    
    def _plot_volume(self, ax, df):
        colors = [self.colors['up'] if row['close'] >= row['open'] 
                 else self.colors['down'] for _, row in df.iterrows()]
        
        ax.bar(df.index, df['tick_volume'], color=colors, alpha=0.6, width=0.8)
    
    def _plot_component_scores(self, ax, metrics_df):
        ax.plot(metrics_df.index, metrics_df['vp_position_score'], 
               color=self.colors['vp_score'], linewidth=1.5, 
               label='VP Score', alpha=0.8)
        
        ax.plot(metrics_df.index, metrics_df['order_flow_score'], 
               color=self.colors['flow_score'], linewidth=1.5, 
               label='Flow Score', alpha=0.8)
        
        ax.plot(metrics_df.index, metrics_df['vwap_relation_score'], 
               color=self.colors['vwap_score'], linewidth=1.5, 
               label='VWAP Score', alpha=0.8)
    
    def _plot_final_scores(self, ax, metrics_df):
        ax.plot(metrics_df.index, metrics_df['raw_score'], 
               color='gray', linewidth=1, label='Raw Score', 
               alpha=0.5, linestyle='--')
        
        ax.plot(metrics_df.index, metrics_df['filtered_score'], 
               color=self.colors['final_score'], linewidth=2, 
               label='Filtered Score', alpha=0.9)
        
        ax.fill_between(metrics_df.index, 0, metrics_df['filtered_score'],
                       where=metrics_df['filtered_score'] > 0,
                       color='green', alpha=0.2)
        ax.fill_between(metrics_df.index, 0, metrics_df['filtered_score'],
                       where=metrics_df['filtered_score'] < 0,
                       color='red', alpha=0.2)

chart_generator = ChartGenerator()