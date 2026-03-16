import argparse
import warnings
import pickle
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score

from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score

try:
    import statsmodels.api as sm
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# 2.  TARGET VARIABLE  (forward OLS slope)
# ══════════════════════════════════════════════════════════════════════════════

def compute_forward_slope(prices: np.ndarray, 
                          window: int = 10) -> np.ndarray:
    """
    At each bar t compute the OLS slope of the NEXT `window` bars.
    This is the mu we want to predict.

    Bar t uses prices[t : t+window] — strictly future data.
    Features at t use prices[:t] — strictly past data.
    The 1-bar shift between features and target prevents lookahead.

    Parameters
    ----------
    prices : array of close prices
    window : forward window W

    Returns
    -------
    slopes : array, NaN for last `window` bars
    """
    n      = len(prices)
    slopes = np.full(n, np.nan)
    idx    = np.arange(window, dtype=float)
    idm    = idx.mean()

    for t in range(n - window):
        y  = prices[t : t + window]
        ym = y.mean()
        cov = np.sum((idx - idm) * (y - ym))
        var = np.sum((idx - idm) ** 2)
        if var > 1e-12:
            slopes[t] = cov / var

    return slopes


# ══════════════════════════════════════════════════════════════════════════════
# 3.  TEMPORAL TRAIN / VAL / TEST SPLIT
# ══════════════════════════════════════════════════════════════════════════════

def temporal_split(X: pd.DataFrame, y: pd.Series,
                   train_frac=0.60, val_frac=0.20):
    """
    Strict temporal split — NO shuffling.
    Last (1 - train_frac - val_frac) fraction is held-out test set.
    """
    n       = len(X)
    n_train = int(n * train_frac)
    n_val   = int(n * val_frac)

    X_train = X.iloc[:n_train]
    y_train = y.iloc[:n_train]

    X_val   = X.iloc[n_train : n_train + n_val]
    y_val   = y.iloc[n_train : n_train + n_val]

    X_test  = X.iloc[n_train + n_val:]
    y_test  = y.iloc[n_train + n_val:]

    print(f"\n  Train : {len(X_train):>6} bars  "
          f"({X_train.index[0]} → {X_train.index[-1]})")
    print(f"  Val   : {len(X_val):>6} bars  "
          f"({X_val.index[0]} → {X_val.index[-1]})")
    print(f"  Test  : {len(X_test):>6} bars  "
          f"({X_test.index[0]} → {X_test.index[-1]})")

    return X_train, y_train, X_val, y_val, X_test, y_test


# ══════════════════════════════════════════════════════════════════════════════
# 4.  WALK-FORWARD CROSS-VALIDATION
# ══════════════════════════════════════════════════════════════════════════════
def walk_forward_cv(X_train: np.ndarray, y_train: np.ndarray,
                    n_splits: int = 5, gap: int = 10):

    tscv = TimeSeriesSplit(n_splits=n_splits, gap=gap)
    fold_results = []

    for fold, (tr_idx, val_idx) in enumerate(tscv.split(X_train)):

        X_tr = X_train[tr_idx]; y_tr = y_train[tr_idx]
        X_v  = X_train[val_idx]; y_v = y_train[val_idx]

        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr)
        X_v_s  = scaler.transform(X_v)

        model = MLPRegressor(
            hidden_layer_sizes=(64,32),
            activation="relu",
            solver="adam",
            learning_rate_init=0.001,
            max_iter=500,
            early_stopping=True,
            validation_fraction=0.15,
            n_iter_no_change=20,
            random_state=42,
            alpha=0.001,
        )

        model.fit(X_tr_s, y_tr)
        y_pred = model.predict(X_v_s)

        mse     = mean_squared_error(y_v, y_pred)
        r2      = r2_score(y_v, y_pred)
        dir_acc = np.mean(np.sign(y_pred) == np.sign(y_v))
        ic, icp = stats.spearmanr(y_pred, y_v)

        fold_results.append(dict(
            fold    = fold + 1,
            mse     = mse,
            r2      = r2,
            dir_acc = dir_acc,
            ic      = ic,
            ic_p    = icp
        ))

        print(f"  Fold {fold+1}  |  "
              f"R²={r2:.4f}  "
              f"DirAcc={dir_acc:.4f}  "
              f"IC={ic:.4f} (p={icp:.3f})")

    return fold_results


# ══════════════════════════════════════════════════════════════════════════════
# 5b.  FIT FINAL MODEL
# ══════════════════════════════════════════════════════════════════════════════

def fit_final_model(X_train: np.ndarray, y_train: np.ndarray,
                    feature_names: list):

    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_train)

    model = MLPRegressor(
        hidden_layer_sizes=(128,64,64,32),
        activation="relu",
        solver="adam",
        learning_rate_init=0.001,
        max_iter=1000,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=30,
        random_state=42
    )

    model.fit(X_tr_s, y_train)

    print("\n  Neural Network architecture:")
    print("  Input → 64 → 32 → 1")

    return scaler, model


# ══════════════════════════════════════════════════════════════════════════════
# 6.  EVALUATION
# ══════════════════════════════════════════════════════════════════════════════

def evaluate(name: str, y_true: np.ndarray, 
             y_pred: np.ndarray, tp: float, sl: float,
             sigma_series: np.ndarray = None):
    """
    Full evaluation suite including Peclet number diagnostic.
    """
    print(f"\n{'─'*55}")
    print(f"  {name}")
    print(f"{'─'*55}")

    # Basic metrics
    mse     = mean_squared_error(y_true, y_pred)
    r2      = r2_score(y_true, y_pred)
    dir_acc = np.mean(np.sign(y_pred) == np.sign(y_true))
    ic, icp = stats.spearmanr(y_pred, y_true)

    # t-test: is mean prediction significantly nonzero?
    t_mu, p_mu = stats.ttest_1samp(y_pred, popmean=0)

    # Null model MSE (always predict zero)
    mse_null = mean_squared_error(y_true, np.zeros_like(y_true))
    improv   = (1 - mse / mse_null) * 100

    print(f"  R²             : {r2:.4f}")
    print(f"  MSE model      : {mse:.8f}")
    print(f"  MSE null       : {mse_null:.8f}")
    print(f"  Improvement    : {improv:.2f}%")
    print(f"  Direction acc  : {dir_acc:.4f}  "
          f"({'above' if dir_acc > 0.5 else 'below'} random)")
    print(f"  IC (Spearman)  : {ic:.4f}  p={icp:.4f}")
    print(f"  t(E[mu]=0)     : {t_mu:.3f}  p={p_mu:.4f}")

    # Peclet number diagnostic
    domain = tp + abs(sl)   # TP - SL
    if sigma_series is not None:
        sigma_mean = np.nanmean(sigma_series)
        pe_vals    = np.abs(y_pred) * domain / (0.5 * sigma_mean**2 + 1e-9)
        print(f"\n  Peclet diagnostic (Pe = |mu|*L / 0.5*sigma²)")
        print(f"  L (domain)     : {domain:.4f}")
        print(f"  sigma mean     : {sigma_mean:.4f}")
        print(f"  Pe mean        : {pe_vals.mean():.4f}")
        print(f"  Pe median      : {np.median(pe_vals):.4f}")
        print(f"  Pe > 10 (%)    : {np.mean(pe_vals > 10)*100:.1f}%  "
              f"← drift dominating, scale mu down")
        print(f"  Pe < 0.1 (%)   : {np.mean(pe_vals < 0.1)*100:.1f}%  "
              f"← mu irrelevant, too small")
        print(f"  Pe in [0.1,10] : {np.mean((pe_vals>=0.1)&(pe_vals<=10))*100:.1f}%  "
              f"← meaningful range")

    # Calibration — binomial test on direction calls
    n_correct = int(dir_acc * len(y_pred))
    binom_res = stats.binomtest(n_correct, len(y_pred), p=0.5)
    binom_p   = binom_res.pvalue
    print(f"\n  Binomial test H0 (dir_acc=0.5): p={binom_p:.4f}")
    if binom_p < 0.05:
        print(f"  ✔  Direction accuracy significantly above random")
    else:
        print(f"  ✗  Direction accuracy NOT significantly above random")

    return dict(r2=r2, mse=mse, mse_null=mse_null,
                improvement=improv, dir_acc=dir_acc,
                ic=ic, ic_p=icp, t_mu=t_mu, p_mu=p_mu)

def load_model(path):
    import pickle
    import json
    from pathlib import Path

    model_dir = Path(path)

    print("\nLoading model...")

    with open(model_dir / "model_model.pkl", "rb") as f:
        model = pickle.load(f)

    with open(model_dir / "scaler.pkl", "rb") as f:
        scaler = pickle.load(f)

    with open(model_dir / "feature_cols.json", "r") as f:
        feature_cols = json.load(f)

    print("Model loaded successfully")
    print(f"Number of features: {len(feature_cols)}")

    return model, scaler, feature_cols

# ══════════════════════════════════════════════════════════════════════════════
# 7.  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main(args = {
        "csv": "m5_data.csv",   # Path to input CSV file
        "tp": 2.0,             # Take-profit in price units
        "sl": 1.5,             # Stop-loss in price units
        "window": 10,          # Forward slope window W
        "gap": 10,             # Gap for walk-forward CV (must >= max feature window)
        "out": "ols_mu_model"  # Output directory for model and diagnostics
    }):

    args = argparse.Namespace(**args)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("="*55)
    print("  OLS Drift (mu) Training Pipeline")
    print("="*55)
    print(f"  TP     : {args.tp}")
    print(f"  SL     : {args.sl}")
    print(f"  Window : {args.window}")

    # ── Load data ─────────────────────────────────────────────────────────────
    print("\n[1/7] Loading data ...")


    if type(args.csv) == pd.DataFrame:
        df = args.csv.copy()
    elif args.csv.endswith(".csv"):
        df = pd.read_csv(args.csv, index_col=0, parse_dates=True)
    else:
        raise ValueError("Invalid input for --csv. Must be path to CSV or DataFrame.")
    
    required = ["open", "high", "low", "close", "volume"]
    missing  = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df.dropna()
    print(f"  Loaded {len(df)} bars")

    # ── Features ──────────────────────────────────────────────────────────────
    print("\n[2/7] Building features ...")
    # feat = build_ohlcv_features(df)
    feat = df.drop(columns=["open", "high", "low", "close", "volume","time"])  # baseline: no features
    print(f"  Built {feat.shape[1]} features")

    # ── Target ────────────────────────────────────────────────────────────────
    print("\n[3/7] Computing forward slope target ...")
    forward_slope = compute_forward_slope(
        df["close"].values, window=args.window)
    target = pd.Series(forward_slope, index=df.index,
                       name="forward_slope")

    # ── Align — shift features by 1 bar to prevent lookahead ─────────────────
    # Feature at t-1 predicts slope starting at t
    feat_shifted = feat.shift(1)

    # Combine and drop NaN rows
    combined = pd.concat([feat_shifted, target], axis=1).dropna()
    feature_cols = [c for c in combined.columns if c != "forward_slope"]

    X = combined[feature_cols]
    y = combined["forward_slope"]

    print(f"  Features : {X.shape[1]}")
    print(f"  Samples  : {X.shape[0]}")
    print(f"  Target mean  : {y.mean():.6f}")
    print(f"  Target std   : {y.std():.6f}")
    print(f"  Target range : [{y.min():.6f}, {y.max():.6f}]")

    # ── Split ─────────────────────────────────────────────────────────────────
    print("\n[4/7] Temporal train/val/test split ...")
    (X_train, y_train,
     X_val,   y_val,
     X_test,  y_test) = temporal_split(X, y)

    X_train_arr = X_train.values
    y_train_arr = y_train.values
    X_val_arr   = X_val.values
    y_val_arr   = y_val.values
    X_test_arr  = X_test.values
    y_test_arr  = y_test.values

    # ── Walk-forward CV ───────────────────────────────────────────────────────
    print("\n[5/7] Walk-forward cross-validation ...")
    cv_results = walk_forward_cv(
        X_train_arr, y_train_arr,
        n_splits=5, gap=args.gap
    )

    cv_r2s  = [r["r2"]      for r in cv_results]
    cv_ics  = [r["ic"]      for r in cv_results]
    cv_dirs = [r["dir_acc"] for r in cv_results]
    # best_alpha = np.median([r["alpha"] for r in cv_results])

    print(f"\n  CV Summary:")
    print(f"  R²       : {np.mean(cv_r2s):.4f} ± {np.std(cv_r2s):.4f}")
    print(f"  IC       : {np.mean(cv_ics):.4f} ± {np.std(cv_ics):.4f}")
    print(f"  Dir Acc  : {np.mean(cv_dirs):.4f} ± {np.std(cv_dirs):.4f}")

    # ── Final model ───────────────────────────────────────────────────────────
    print("\n[6/7] Fitting final model ...")
    scaler, model = fit_final_model(
        X_train_arr, y_train_arr, feature_cols)

    # ── Evaluate on val and test ──────────────────────────────────────────────
    print("\n[7/7] Evaluation ...")

    # Val set
    X_val_s  = scaler.transform(X_val_arr)
    y_val_pred = model.predict(X_val_s)
    sigma_val  = X_val[f"hvol_{10}"].values if f"hvol_{10}" in X_val.columns else None

    val_metrics = evaluate(
        "VALIDATION SET", y_val_arr, y_val_pred,
        args.tp, args.sl, sigma_val)

    # Test set — only touched once
    print("\n  *** FINAL TEST SET EVALUATION ***")
    print("  (This is the honest number — only evaluated once)")
    X_test_s   = scaler.transform(X_test_arr)
    y_test_pred = model.predict(X_test_s)
    sigma_test  = X_test[f"hvol_{10}"].values if f"hvol_{10}" in X_test.columns else None

    test_metrics = evaluate(
        "TEST SET (FINAL)", y_test_arr, y_test_pred,
        args.tp, args.sl, sigma_test)

    # ── Save ──────────────────────────────────────────────────────────────────
    print(f"\n  Saving model to {out_dir}/")

    with open(out_dir / "model_model.pkl", "wb") as f:
        pickle.dump(model, f)

    with open(out_dir / "scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    with open(out_dir / "feature_cols.json", "w") as f:
        json.dump(feature_cols, f, indent=2)

    meta = dict(
        window      = args.window,
        tp          = args.tp,
        sl          = args.sl,
        n_features  = len(feature_cols),
        cv_r2_mean  = float(np.mean(cv_r2s)),
        cv_ic_mean  = float(np.mean(cv_ics)),
        val_metrics = val_metrics,
        test_metrics= test_metrics,
    )
    with open(out_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"  ✔  model_model.pkl")
    print(f"  ✔  scaler.pkl")
    print(f"  ✔  feature_cols.json  ({len(feature_cols)} features)")
    print(f"  ✔  meta.json")


if __name__ == "__main__":
    main()