from statistical_modeling.Risk_Modeling import build_risk_features
from statistical_modeling.risk_dashboard import plot_risk_dashboard
from ols import main as ols_main
from ols import load_model
from pde_backtest import main as pde_main
from data_fetcher import data_fetcher
from config_loader import config

if not data_fetcher.connect():
    raise Exception("Failed to connect to MT5")

timeframe = config.get('trading', 'active_timeframe')
timeframe = timeframe if isinstance(timeframe, list) else [timeframe]

tf_data = {}
for tf in timeframe:
    print(f"Fetching data for timeframe: {tf} ...")
    df = data_fetcher.fetch_data(tf)
    print(f"Fetched {len(df)} rows of data for {tf} timeframe.")
    df.rename(columns={'open_time': 'time'}, inplace=True)
    df.rename(columns={'tick_volume': 'volume'}, inplace=True)
    df = build_risk_features(df, tf)
    tf_data[tf] = df

    ols_main(args = {
        "csv": tf_data[tf].copy(),   # Path to input CSV file
        "tp": 5.5,             # Take-profit in price units
        "sl": 4,             # Stop-loss in price units
        "window": 10,          # Forward slope window W
        "gap": 10,             # Gap for walk-forward CV (must >= max feature window)
        "out": f"advanced/{tf}/pde_model"  # Output directory for model and diagnostics
    })

    model, scalar, feature_cols = load_model(f"advanced/{tf}/pde_model")
    tf_data[tf]['mu_pred'] = model.predict(scalar.transform(tf_data[tf][feature_cols].fillna(0).values))

    # Backtest from PDE and trained OLS model
    pde_bt, pde_path_df = pde_main(args = {
        "csv": tf_data[tf].copy(),   # Path to input CSV file
        "tp": 5.5,              # Take-profit in price units
        "sl": 4,                # Stop-loss in price units
        "mu_col": "mu_pred",          
        "threshold": 1,             
        "out": f"advanced/{tf}/pde_model"  # Output directory for model and diagnostics
    })

    plot_risk_dashboard(
        tf_data[tf], 
        tag=tf,
        save_path=f"advanced/{tf}/risk_dashboard.png"
    )
