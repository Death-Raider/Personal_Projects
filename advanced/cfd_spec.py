def pts_to_usd(pts, symbol, lots):
    import MetaTrader5 as mt5
    info = mt5.symbol_info(symbol)
    return pts * (info.trade_tick_value / info.trade_tick_size) * lots