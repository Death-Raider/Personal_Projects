import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import MetaTrader5 as mt5

# Import the new modules
from volume_volatility_analysis import (
    VolumeAnalyzer, 
    VolatilityAnalyzer, 
    LiquidityAnalyzer,
    add_volume_metrics,
    add_volatility_metrics,
    add_liquidity_metrics
)

def calculate_annualization_factor(timeframe: int) -> int:
    """
    Calculate annualization factor based on timeframe
    
    Args:
        timeframe: MT5 timeframe constant (e.g., mt5.TIMEFRAME_M5)
    
    Returns:
        Annualization factor for volatility calculations
    """
    timeframe_map = {
        mt5.TIMEFRAME_M1: 525600,   # 252 * 24 * 60
        mt5.TIMEFRAME_M5: 105120,   # 252 * 24 * 12
        mt5.TIMEFRAME_M15: 35040,   # 252 * 24 * 4
        mt5.TIMEFRAME_M30: 17520,   # 252 * 24 * 2
        mt5.TIMEFRAME_H1: 8760,     # 252 * 24
        mt5.TIMEFRAME_H4: 2190,     # 252 * 6
        mt5.TIMEFRAME_D1: 252,      # 252 trading days
    }
    
    return timeframe_map.get(timeframe, 72576)  # Default to M5 if unknown

def add_advanced_metrics(df: pd.DataFrame, timeframe: int) -> pd.DataFrame:
    """
    Add advanced metrics to the DataFrame for comprehensive analysis
    
    Args:
        df: Original DataFrame with price data
        timeframe: MT5 timeframe constant for annualization factor
    """
    price_bins=50
    volume_profile_lookback = 200


    annualization_factor = calculate_annualization_factor(timeframe)
    df = add_volume_metrics(df)
    df = add_volatility_metrics(df, annualization_factor)
    df = add_liquidity_metrics(df)

    vol_analyzer = VolumeAnalyzer(price_bins=price_bins)
    vol_profile = vol_analyzer.calculate_volume_profile(df, lookback=volume_profile_lookback)
    vpoc = vol_analyzer.get_vpoc(vol_profile)
    val, vah = vol_analyzer.get_value_area(vol_profile, value_area_pct=70.0)

    vol_analyzer_cone = VolatilityAnalyzer(annualization_factor)
    vol_cone = vol_analyzer_cone.calculate_volatility_cone(
        df, periods=[5, 10, 20, 50, 100]
    )
    return {
        'df': df,
        'volume_profile': vol_profile,
        'vpoc': vpoc,
        'val': val,
        'vah': vah,
        'vol_cone': vol_cone
    }

def generate_summary(df):
    print("\nKEY STATISTICS (Last 100 bars):")
    recent_df = df.tail(100)
    
    print(f"\nVolume Metrics:")
    print(f"  Avg Relative Volume: {recent_df['relative_volume'].mean():.2f}x")
    print(f"  Cumulative Delta: {recent_df['cumulative_delta'].iloc[-1]:.0f}")
    print(f"  Current vs VWAP: {((recent_df['close'].iloc[-1] / recent_df['vwap'].iloc[-1]) - 1) * 100:.2f}%")
    
    print(f"\nVolatility Metrics:")
    print(f"  Realized Vol (Close): {recent_df['realized_vol_close'].mean():.2f}%")
    print(f"  Implied Vol (ATR): {recent_df['implied_vol_proxy'].mean():.2f}%")
    print(f"  Avg VRP: {recent_df['vol_risk_premium'].mean():.2f}%")
    
    print(f"\nLiquidity Metrics:")
    print(f"  Efficiency Ratio: {recent_df['efficiency_ratio'].mean():.2f}")
    print(f"  Amihud Illiquidity: {recent_df['amihud_illiquidity'].mean():.2f}")