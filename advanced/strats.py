from data_fetcher import data_fetcher
from config_loader import config
from metrics_calculator import metrics_calculator

import pandas as pd
import numpy as np
import time

from backtest_engine import BacktestEngine 
from trade_visualizer import TradeVisualizer, visualize_backtest

if not data_fetcher.connect():
    raise Exception("Failed to connect to MT5")

timeframe = config.get('trading', 'active_timeframe')

m5_df = data_fetcher.fetch_data(timeframe)
m5_df = metrics_calculator.calculate_all_metrics(m5_df, timeframe)

h1_df = data_fetcher.fetch_data('H1')
h1_df = metrics_calculator.calculate_all_metrics(h1_df, 'H1')

h4_df = data_fetcher.fetch_data('H4')
h4_df = metrics_calculator.calculate_all_metrics(h4_df, 'H4')

m5_df.rename(columns={'open_time': 'time'}, inplace=True)
h1_df.rename(columns={'open_time': 'time'}, inplace=True)
h4_df.rename(columns={'open_time': 'time'}, inplace=True)

m5_df.rename(columns={'tick_volume': 'volume'}, inplace=True)
h1_df.rename(columns={'tick_volume': 'volume'}, inplace=True)
h4_df.rename(columns={'tick_volume': 'volume'}, inplace=True)


from statistical_modeling.Risk_Modeling import build_risk_features
from statistical_modeling.risk_dashboard import plot_risk_dashboard

df = {
    'M5': build_risk_features(m5_df, 'M5'),
    'H1': build_risk_features(h1_df, 'H1'),
    'H4': build_risk_features(h4_df, 'H4')
}
for keys in df.keys():
    plot_risk_dashboard(df[keys], tag=keys,
                        save_path=f"advanced/statistical_modeling/risk_dashboard_{keys}.png")
# engine = BacktestEngine()
# trades, equity = engine.run_backtest(
#     m5_df, 'M5',
#     use_mtf=True,
#     h1_df=h1_df,
#     h4_df=h4_df
# )


# df = pd.DataFrame(trades)
# print(df)
# df['signal'] = df['direction'].apply(lambda x: 1 if x == 'long' else -1)
# df['strength'] = df['strength']*df['signal']
# print(df[['pnl','strength', 'signal', 'direction']])
# print(df[['pnl','strength']].corr())

# # Signed correlation (already done, but for completeness)
# corr_signed = df[['pnl', 'strength']].corr().iloc[0, 1]
# print("Corr(pnl, strength):", corr_signed)

# # Absolute strength vs pnl magnitude
# corr_abs = np.corrcoef(df['pnl'].abs(), df['strength'].abs())[0, 1]
# print("Corr(|pnl|, |strength|):", corr_abs)

# # Direction-aligned strength
# aligned_strength = np.sign(df['strength']) * np.abs(df['strength'])
# corr_aligned = np.corrcoef(df['pnl'], aligned_strength)[0, 1]
# print("Corr(pnl, aligned_strength):", corr_aligned)

# df['abs_strength'] = df['strength'].abs()

# bins = [0, 0.15, 0.30, 0.45, df['abs_strength'].max()]
# labels = ['very_low', 'low', 'medium', 'high']

# df['strength_bucket'] = pd.cut(df['abs_strength'], bins=bins, labels=labels, include_lowest=True)

# bucket_stats = df.groupby('strength_bucket').agg(
#     trades=('pnl', 'count'),
#     avg_pnl=('pnl', 'mean'),
#     win_rate=('pnl', lambda x: (x > 0).mean()),
#     avg_win=('pnl', lambda x: x[x > 0].mean()),
#     avg_loss=('pnl', lambda x: x[x < 0].mean())
# )

# print(bucket_stats)

# df['quantile_bucket'] = pd.qcut(df['abs_strength'], q=5, labels=False)

# quantile_stats = df.groupby('quantile_bucket').agg(
#     trades=('pnl', 'count'),
#     avg_pnl=('pnl', 'mean'),
#     win_rate=('pnl', lambda x: (x > 0).mean()),
#     avg_win=('pnl', lambda x: x[x > 0].mean()),
#     avg_loss=('pnl', lambda x: x[x < 0].mean())
# )

# print(quantile_stats)

# longs = df[df['strength'] > 0]
# shorts = df[df['strength'] < 0]

# print("Long corr:", longs[['pnl', 'strength']].corr().iloc[0, 1])
# print("Short corr:", shorts[['pnl', 'strength']].corr().iloc[0, 1])

# mean_return = df['pnl'].mean()
# std_return = df['pnl'].std()

# sharpe = mean_return / std_return * np.sqrt(len(df))
# print("Trade Sharpe (unnormalized by time):", sharpe)

# extreme_df = df[df['abs_strength'] > 0.45]

# print("Extreme trades:", len(extreme_df))
# print("Extreme avg pnl:", extreme_df['pnl'].mean())
# print("Extreme win rate:", (extreme_df['pnl'] > 0).mean())