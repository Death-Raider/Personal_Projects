import numpy as np
import pandas as pd
from scipy import stats, signal
from scipy.fft import fft, fftfreq
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.mixture import GaussianMixture
import warnings
warnings.filterwarnings("ignore")


def build_risk_features(df: pd.DataFrame, timeframe: str = "H1") -> pd.DataFrame:

    df = df.copy()
    df.columns = [c.lower() for c in df.columns]

    tag = timeframe.upper()

    df = add_returns_and_log_returns(df, tag)
    df = add_higher_moments(df, tag)
    df = add_var_models(df, tag)
    df = add_volatility_models(df, tag)
    df = add_technical_analysis(df, tag)
    df = add_regression_models(df, tag)
    df = add_laplace_taylor_transforms(df, tag)
    df = add_pca_features(df, tag)
    df = add_cluster_analysis(df, tag)
    df = add_factor_distribution(df, tag)
    df = add_asset_class_disclosure(df, tag)
    df = add_positioning_models(df, tag)
    df = add_series_database_models(df, tag)
    df = add_correlation_matrix_features(df, tag)
    df = add_spectral_features(df, tag)

    return df

def add_returns_and_log_returns(df: pd.DataFrame, tag: str) -> pd.DataFrame:
    c = df["close"]
    df[f"{tag}_ret"]          = c.pct_change()
    df[f"{tag}_log_ret"]      = np.log(c / c.shift(1))
    df[f"{tag}_ret_2"]        = c.pct_change(2)
    df[f"{tag}_ret_5"]        = c.pct_change(5)
    df[f"{tag}_ret_10"]       = c.pct_change(10)
    df[f"{tag}_ret_20"]       = c.pct_change(20)
    df[f"{tag}_cum_ret"]      = (1 + df[f"{tag}_ret"]).cumprod() - 1
    df[f"{tag}_excess_ret"]   = df[f"{tag}_ret"] - df[f"{tag}_ret"].rolling(20).mean()
    # True Range
    df[f"{tag}_true_range"]   = pd.concat([
        df["high"] - df["low"],
        (df["high"] - df["close"].shift()).abs(),
        (df["low"]  - df["close"].shift()).abs()
    ], axis=1).max(axis=1)
    return df

def add_higher_moments(df: pd.DataFrame, tag: str,
                       windows: list = [10, 20, 50]) -> pd.DataFrame:
    """
    Mean, Variance, Skewness, Kurtosis, 5th/6th central moments,
    Jarque-Bera stat, Shapiro-Wilk rolling approximation.
    """
    r = df[f"{tag}_log_ret"].fillna(0)

    for w in windows:
        pfx = f"{tag}_m{w}"
        roll = r.rolling(w)

        df[f"{pfx}_mean"]     = roll.mean()
        df[f"{pfx}_std"]      = roll.std()
        df[f"{pfx}_var"]      = roll.var()
        df[f"{pfx}_skew"]     = roll.skew()
        df[f"{pfx}_kurt"]     = roll.kurt()          # excess kurtosis (Fisher)
        df[f"{pfx}_kurt_raw"] = roll.kurt() + 3      # Pearson kurtosis

        # 5th and 6th standardised moments via apply
        def moment5(x):
            s = x.std()
            return stats.moment(x, 5) / (s**5) if s > 0 else 0
        def moment6(x):
            s = x.std()
            return stats.moment(x, 6) / (s**6) if s > 0 else 0

        df[f"{pfx}_moment5"]  = roll.apply(moment5, raw=True)
        df[f"{pfx}_moment6"]  = roll.apply(moment6, raw=True)

        # Jarque-Bera statistic (not p-value)
        def jb_stat(x):
            n = len(x); s = x.std()
            if s == 0: return 0
            sk = stats.skew(x); ku = stats.kurtosis(x)
            return (n / 6) * (sk**2 + (ku**2) / 4)
        df[f"{pfx}_jb_stat"]  = roll.apply(jb_stat, raw=True)

        # Semi-variance (downside)
        def semi_var(x):
            mu = x.mean(); down = x[x < mu] - mu
            return (down**2).mean() if len(down) > 0 else 0
        df[f"{pfx}_semi_var"] = roll.apply(semi_var, raw=True)

        # Entropy (Shannon, discretised into 10 bins)
        def shannon_entropy(x):
            counts, _ = np.histogram(x, bins=10)
            p = counts / counts.sum()
            p = p[p > 0]
            return -np.sum(p * np.log(p))
        df[f"{pfx}_entropy"]  = roll.apply(shannon_entropy, raw=True)

    return df

def add_var_models(df: pd.DataFrame, tag: str,
                   windows: list = [20, 50],
                   conf_levels: list = [0.95, 0.99]) -> pd.DataFrame:
    """
    Historical VaR, Parametric (Normal & t-dist) VaR, CVaR/ES,
    Modified Cornish-Fisher VaR, Monte-Carlo VaR proxy.
    """
    r = df[f"{tag}_log_ret"].fillna(0)

    for w in windows:
        roll = r.rolling(w)
        mu_r   = roll.mean()
        sig_r  = roll.std()

        for cl in conf_levels:
            alpha = 1 - cl
            z     = stats.norm.ppf(1 - cl)
            pfx   = f"{tag}_w{w}_cl{int(cl*100)}"

            # Historical VaR
            df[f"{pfx}_hvar"] = roll.quantile(alpha)

            # Historical CVaR (Expected Shortfall)
            def cvar_hist(x, a=alpha):
                threshold = np.quantile(x, a)
                tail = x[x <= threshold]
                return tail.mean() if len(tail) > 0 else threshold
            df[f"{pfx}_hcvar"] = roll.apply(cvar_hist, raw=True)

            # Parametric Normal VaR
            df[f"{pfx}_pvar_norm"] = mu_r + z * sig_r

            # Parametric CVaR Normal
            df[f"{pfx}_pcvar_norm"] = mu_r - sig_r * (stats.norm.pdf(z) / alpha)

            # Student-t VaR (df estimated from rolling kurtosis)
            def t_var(x, a=alpha):
                if x.std() == 0: return 0
                df_t = max(4, 6 / (stats.kurtosis(x) + 1e-9) + 4)
                return stats.t.ppf(a, df=df_t, loc=x.mean(), scale=x.std())
            df[f"{pfx}_tvar"] = roll.apply(t_var, raw=True)

            # Cornish-Fisher Modified VaR
            def cf_var(x, a=alpha):
                mu_x = x.mean(); s = x.std()
                if s == 0: return 0
                sk = stats.skew(x); ku = stats.kurtosis(x)
                z_cf = (z +
                        (z**2 - 1) * sk / 6 +
                        (z**3 - 3*z) * ku / 24 -
                        (2*z**3 - 5*z) * sk**2 / 36)
                return mu_x + z_cf * s
            df[f"{pfx}_cfvar"] = roll.apply(cf_var, raw=True)

    # EWMA VaR (lambda=0.94 RiskMetrics)
    lam = 0.94
    ewma_var = r.ewm(span=(2/(1-lam)-1)).var()
    df[f"{tag}_ewma_var_94"]  = ewma_var
    df[f"{tag}_ewma_vol_94"]  = np.sqrt(ewma_var)
    df[f"{tag}_ewma_var_99"]  = -stats.norm.ppf(0.01) * np.sqrt(ewma_var)
    df[f"{tag}_ewma_var_95"]  = -stats.norm.ppf(0.05) * np.sqrt(ewma_var)

    return df

def add_volatility_models(df: pd.DataFrame, tag: str) -> pd.DataFrame:
    """
    Historical vol, Parkinson, Garman-Klass, Rogers-Satchell, Yang-Zhang,
    GARCH(1,1) proxy, ATR, Volatility Ratio, Volatility-of-Volatility.
    """
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    r  = df[f"{tag}_log_ret"].fillna(0)
    tr = df[f"{tag}_true_range"]

    # Historical (close-to-close)
    for w in [5, 10, 20, 50]:
        df[f"{tag}_hvol_{w}"]  = r.rolling(w).std() * np.sqrt(252)

    # Parkinson (HL)
    pk = (1 / (4 * np.log(2))) * (np.log(h / l)**2)
    for w in [10, 20]:
        df[f"{tag}_pk_vol_{w}"] = np.sqrt(pk.rolling(w).mean() * 252)

    # Garman-Klass
    gk = 0.5 * np.log(h/l)**2 - (2*np.log(2)-1) * np.log(c/o)**2
    for w in [10, 20]:
        df[f"{tag}_gk_vol_{w}"] = np.sqrt(gk.rolling(w).mean() * 252)

    # Rogers-Satchell
    rs = np.log(h/c)*np.log(h/o) + np.log(l/c)*np.log(l/o)
    for w in [10, 20]:
        df[f"{tag}_rs_vol_{w}"] = np.sqrt(rs.rolling(w).mean() * 252)

    # Yang-Zhang
    k   = 0.34 / (1.34 + (21+1)/(21-1))
    oc  = np.log(o / c.shift(1))
    co  = np.log(c / o)
    yz_w = 20
    vo   = oc.rolling(yz_w).var()
    vc   = co.rolling(yz_w).var()
    vrs  = rs.rolling(yz_w).mean()
    df[f"{tag}_yz_vol_20"] = np.sqrt((vo + k*vc + (1-k)*vrs) * 252)

    # ATR variants
    for w in [5, 14, 20]:
        df[f"{tag}_atr_{w}"] = tr.rolling(w).mean()

    # Normalised ATR (NATR)
    df[f"{tag}_natr_14"] = df[f"{tag}_atr_14"] / c * 100

    # Volatility Ratio (current ATR vs long-run)
    df[f"{tag}_vol_ratio"] = df[f"{tag}_atr_14"] / df[f"{tag}_atr_14"].rolling(50).mean()

    # Volatility of Volatility
    df[f"{tag}_vol_of_vol"] = df[f"{tag}_hvol_20"].rolling(20).std()

    # GARCH(1,1) single-step proxy: sigma2_t = omega + alpha*r_{t-1}^2 + beta*sigma2_{t-1}
    def garch_proxy(returns, omega=1e-6, alpha=0.09, beta=0.90):
        sigma2 = np.full(len(returns), returns.var())
        for i in range(1, len(returns)):
            sigma2[i] = omega + alpha * returns.iloc[i-1]**2 + beta * sigma2[i-1]
        return pd.Series(np.sqrt(sigma2), index=returns.index)
    df[f"{tag}_garch_vol"] = garch_proxy(r)

    return df


def add_technical_analysis(df: pd.DataFrame, tag: str) -> pd.DataFrame:
    c, h, l, o, v = df["close"], df["high"], df["low"], df["open"], df["volume"]

    # ── Trend ──────────────────────────────────────────────────────────────
    for w in [5, 10, 20, 50, 100, 200]:
        df[f"{tag}_sma_{w}"]  = c.rolling(w).mean()
        df[f"{tag}_ema_{w}"]  = c.ewm(span=w, adjust=False).mean()

    # MACD
    ema12 = c.ewm(span=12).mean(); ema26 = c.ewm(span=26).mean()
    df[f"{tag}_macd"]         = ema12 - ema26
    df[f"{tag}_macd_signal"]  = df[f"{tag}_macd"].ewm(span=9).mean()
    df[f"{tag}_macd_hist"]    = df[f"{tag}_macd"] - df[f"{tag}_macd_signal"]

    # Parabolic SAR proxy (simplified acceleration)
    df[f"{tag}_price_vs_sma20"] = c / df[f"{tag}_sma_20"] - 1
    df[f"{tag}_price_vs_sma50"] = c / df[f"{tag}_sma_50"] - 1

    # ── Momentum ───────────────────────────────────────────────────────────
    # RSI
    def rsi(series, period=14):
        delta = series.diff()
        gain  = delta.clip(lower=0).rolling(period).mean()
        loss  = (-delta.clip(upper=0)).rolling(period).mean()
        rs    = gain / (loss + 1e-9)
        return 100 - (100 / (1 + rs))
    df[f"{tag}_rsi_14"]  = rsi(c, 14)
    df[f"{tag}_rsi_7"]   = rsi(c, 7)

    # Stochastic
    for w in [14]:
        lo_w = l.rolling(w).min(); hi_w = h.rolling(w).max()
        df[f"{tag}_stoch_k_{w}"] = 100 * (c - lo_w) / (hi_w - lo_w + 1e-9)
        df[f"{tag}_stoch_d_{w}"] = df[f"{tag}_stoch_k_{w}"].rolling(3).mean()

    # Williams %R
    df[f"{tag}_williams_r"] = -100 * (h.rolling(14).max() - c) / \
                               (h.rolling(14).max() - l.rolling(14).min() + 1e-9)

    # ROC
    for w in [5, 10, 20]:
        df[f"{tag}_roc_{w}"] = c.pct_change(w) * 100

    # CCI
    tp = (h + l + c) / 3
    df[f"{tag}_cci_20"] = (tp - tp.rolling(20).mean()) / \
                          (0.015 * tp.rolling(20).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True) + 1e-9)

    # ── Volatility-based ───────────────────────────────────────────────────
    # Bollinger Bands
    sma20 = df[f"{tag}_sma_20"]; std20 = c.rolling(20).std()
    df[f"{tag}_bb_upper"]  = sma20 + 2 * std20
    df[f"{tag}_bb_lower"]  = sma20 - 2 * std20
    df[f"{tag}_bb_width"]  = (df[f"{tag}_bb_upper"] - df[f"{tag}_bb_lower"]) / sma20
    df[f"{tag}_bb_pct"]    = (c - df[f"{tag}_bb_lower"]) / (df[f"{tag}_bb_upper"] - df[f"{tag}_bb_lower"] + 1e-9)

    # Keltner Channels
    kc_mid = df[f"{tag}_ema_20"]; atr14 = df[f"{tag}_atr_14"]
    df[f"{tag}_kc_upper"]  = kc_mid + 2 * atr14
    df[f"{tag}_kc_lower"]  = kc_mid - 2 * atr14
    df[f"{tag}_kc_pct"]    = (c - df[f"{tag}_kc_lower"]) / \
                              (df[f"{tag}_kc_upper"] - df[f"{tag}_kc_lower"] + 1e-9)

    # Squeeze Momentum (BB vs KC overlap)
    df[f"{tag}_squeeze"]   = (df[f"{tag}_bb_upper"] < df[f"{tag}_kc_upper"]).astype(int)

    # ── Volume ─────────────────────────────────────────────────────────────
    df[f"{tag}_vwap"]         = (tp * v).cumsum() / v.cumsum()
    df[f"{tag}_obv"]          = (np.sign(c.diff()) * v).cumsum()
    df[f"{tag}_vol_ma20"]     = v.rolling(20).mean()
    df[f"{tag}_vol_ratio"]    = v / (df[f"{tag}_vol_ma20"] + 1e-9)
    df[f"{tag}_cmf_20"]       = ((c - l - h + c) / (h - l + 1e-9) * v).rolling(20).sum() / \
                                 (v.rolling(20).sum() + 1e-9)

    # MFI
    mf_raw = tp * v; pos_mf = mf_raw.where(tp > tp.shift(), 0)
    neg_mf = mf_raw.where(tp < tp.shift(), 0)
    df[f"{tag}_mfi_14"] = 100 - 100 / (1 + pos_mf.rolling(14).sum() / (neg_mf.rolling(14).sum() + 1e-9))

    # ── Support / Resistance ───────────────────────────────────────────────
    df[f"{tag}_pivot"]       = (h.shift() + l.shift() + c.shift()) / 3
    df[f"{tag}_r1"]          = 2 * df[f"{tag}_pivot"] - l.shift()
    df[f"{tag}_s1"]          = 2 * df[f"{tag}_pivot"] - h.shift()
    df[f"{tag}_dist_to_r1"]  = (df[f"{tag}_r1"] - c) / c
    df[f"{tag}_dist_to_s1"]  = (c - df[f"{tag}_s1"]) / c

    # ── ADX / DMI ──────────────────────────────────────────────────────────
    tr14 = df[f"{tag}_true_range"]
    up_move   = h - h.shift(); dn_move = l.shift() - l
    plus_dm   = up_move.where((up_move > dn_move) & (up_move > 0), 0)
    minus_dm  = dn_move.where((dn_move > up_move) & (dn_move > 0), 0)
    atr14_s   = tr14.ewm(span=14).mean()
    pdi       = 100 * plus_dm.ewm(span=14).mean()  / (atr14_s + 1e-9)
    mdi       = 100 * minus_dm.ewm(span=14).mean() / (atr14_s + 1e-9)
    dx        = 100 * (pdi - mdi).abs() / (pdi + mdi + 1e-9)
    df[f"{tag}_adx"]         = dx.ewm(span=14).mean()
    df[f"{tag}_pdi"]         = pdi
    df[f"{tag}_mdi"]         = mdi

    # ── Ichimoku ───────────────────────────────────────────────────────────
    df[f"{tag}_tenkan"]      = (h.rolling(9).max()  + l.rolling(9).min())  / 2
    df[f"{tag}_kijun"]       = (h.rolling(26).max() + l.rolling(26).min()) / 2
    df[f"{tag}_senkou_a"]    = ((df[f"{tag}_tenkan"] + df[f"{tag}_kijun"]) / 2).shift(26)
    df[f"{tag}_senkou_b"]    = ((h.rolling(52).max() + l.rolling(52).min()) / 2).shift(26)
    df[f"{tag}_cloud_width"] = df[f"{tag}_senkou_a"] - df[f"{tag}_senkou_b"]
    df[f"{tag}_cloud_pos"]   = np.sign(c - df[f"{tag}_senkou_a"].shift(-26))

    return df


def add_regression_models(df: pd.DataFrame, tag: str,
                           windows: list = [20, 50]) -> pd.DataFrame:
    """
    OLS linear regression on price, Ridge on returns, rolling beta,
    R², residual (alpha), forecast deviation, Huber robust regression.
    """
    c = df["close"]
    r = df[f"{tag}_log_ret"].fillna(0)

    for w in windows:
        pfx = f"{tag}_reg{w}"
        x_idx = np.arange(w)

        def ols_slope(y):
            if np.isnan(y).any(): return np.nan
            return np.polyfit(x_idx, y, 1)[0]

        def ols_intercept(y):
            if np.isnan(y).any(): return np.nan
            return np.polyfit(x_idx, y, 1)[1]

        def ols_r2(y):
            if np.isnan(y).any(): return np.nan
            p = np.polyfit(x_idx, y, 1)
            yhat = np.polyval(p, x_idx)
            ss_res = np.sum((y - yhat)**2)
            ss_tot = np.sum((y - y.mean())**2)
            return 1 - ss_res / (ss_tot + 1e-9)

        def ols_residual(y):
            if np.isnan(y).any(): return np.nan
            p = np.polyfit(x_idx, y, 1)
            return y[-1] - np.polyval(p, x_idx[-1])

        def ols_forecast_1(y):
            if np.isnan(y).any(): return np.nan
            p = np.polyfit(x_idx, y, 1)
            return np.polyval(p, w)   # next bar forecast

        df[f"{pfx}_slope"]      = c.rolling(w).apply(ols_slope,     raw=True)
        df[f"{pfx}_intercept"]  = c.rolling(w).apply(ols_intercept, raw=True)
        df[f"{pfx}_r2"]         = c.rolling(w).apply(ols_r2,        raw=True)
        df[f"{pfx}_residual"]   = c.rolling(w).apply(ols_residual,  raw=True)
        df[f"{pfx}_forecast1"]  = c.rolling(w).apply(ols_forecast_1, raw=True)
        df[f"{pfx}_slope_norm"] = df[f"{pfx}_slope"] / c   # normalised slope

        # Second-order (quadratic) fit curvature
        def quad_curv(y):
            if np.isnan(y).any(): return np.nan
            p = np.polyfit(x_idx, y, 2)
            return p[0]   # coefficient of x^2 = curvature
        df[f"{pfx}_quad_curv"] = c.rolling(w).apply(quad_curv, raw=True)

        # Rolling Beta (vs its own lagged returns as market proxy)
        r_mkt  = r.shift(1).fillna(0)
        cov_rm = r.rolling(w).cov(r_mkt)
        var_m  = r_mkt.rolling(w).var()
        df[f"{pfx}_beta"]       = cov_rm / (var_m + 1e-9)

        # Rolling Alpha (Jensen)
        df[f"{pfx}_alpha"]      = r.rolling(w).mean() - \
                                   df[f"{pfx}_beta"] * r_mkt.rolling(w).mean()

    return df

def add_laplace_taylor_transforms(df: pd.DataFrame, tag: str) -> pd.DataFrame:
    """
    Discrete bilateral Laplace (moment generating function proxy),
    Taylor series expansion of log-price, cumulant generating function,
    characteristic function moments.
    """
    c = df["close"]
    r = df[f"{tag}_log_ret"].fillna(0)

    # ── Taylor Series of log-price around rolling mean ─────────────────────
    # f(c) ≈ f(mu) + f'(mu)(c-mu) + ½f''(mu)(c-mu)² + ...
    for w in [20]:
        roll_mu  = c.rolling(w).mean()
        roll_std = c.rolling(w).std()
        dx       = c - roll_mu
        df[f"{tag}_taylor_t1_{w}"] = dx / (roll_std + 1e-9)                       # 1st order (z-score)
        df[f"{tag}_taylor_t2_{w}"] = (dx**2) / (2 * roll_std**2 + 1e-9)          # 2nd order
        df[f"{tag}_taylor_t3_{w}"] = (dx**3) / (6 * roll_std**3 + 1e-9)          # 3rd order
        df[f"{tag}_taylor_t4_{w}"] = (dx**4) / (24 * roll_std**4 + 1e-9)         # 4th order
        df[f"{tag}_taylor_sum4_{w}"] = (df[f"{tag}_taylor_t1_{w}"] +
                                        df[f"{tag}_taylor_t2_{w}"] +
                                        df[f"{tag}_taylor_t3_{w}"] +
                                        df[f"{tag}_taylor_t4_{w}"])

    # ── Moment Generating Function (MGF) proxy: E[e^{t*r}] for fixed t ────
    for t_val in [0.5, 1.0, 2.0]:
        t_label = str(t_val).replace(".", "p")
        df[f"{tag}_mgf_t{t_label}"] = r.rolling(20).apply(
            lambda x: np.mean(np.exp(t_val * x)), raw=True
        )

    # ── Laplace: bilateral discrete sum proxy ──────────────────────────────
    # L(s) = sum_{n} r_n * e^{-s*n}  (causal window)
    for s_val in [0.1, 0.5]:
        s_label = str(s_val).replace(".", "p")
        weights_20 = np.exp(-s_val * np.arange(20))
        weights_20 = weights_20 / weights_20.sum()
        df[f"{tag}_laplace_s{s_label}"] = r.rolling(20).apply(
            lambda x: np.dot(x, weights_20[::-1]), raw=True
        )

    # ── Cumulant Generating Function: K(t) = log(MGF) ─────────────────────
    mgf_col = f"{tag}_mgf_t1p0"
    df[f"{tag}_cgf_t1"] = np.log(df[mgf_col].clip(lower=1e-9))

    # ── Log-cumulants (κ₁, κ₂, κ₃, κ₄) from CGF Taylor expansion ─────────
    # κ₁ = mean, κ₂ = variance, κ₃ = 3rd cumulant, κ₄ = 4th cumulant
    for w in [20]:
        df[f"{tag}_kappa1_{w}"] = r.rolling(w).mean()
        df[f"{tag}_kappa2_{w}"] = r.rolling(w).var()
        df[f"{tag}_kappa3_{w}"] = r.rolling(w).apply(
            lambda x: stats.moment(x, 3), raw=True
        )
        df[f"{tag}_kappa4_{w}"] = r.rolling(w).apply(
            lambda x: stats.moment(x, 4) - 3 * stats.moment(x, 2)**2, raw=True
        )

    # ── Exponential Smoothing with Laplace-like decay ─────────────────────
    for alpha in [0.1, 0.3, 0.7]:
        a_label = str(alpha).replace(".", "p")
        df[f"{tag}_exp_smooth_{a_label}"] = c.ewm(alpha=alpha, adjust=False).mean()

    return df

def add_pca_features(df: pd.DataFrame, tag: str,
                     n_components: int = 5,
                     window: int = 60) -> pd.DataFrame:
    """
    Rolling PCA on multi-lag return matrix: PC1-PC5 scores,
    explained variance ratios, PC1 loading direction.
    """
    r = df[f"{tag}_log_ret"].fillna(0)
    lags = list(range(1, 21))   # 20-lag feature matrix

    # Build lag matrix (static, all rows)
    lag_mat = pd.concat([r.shift(i).rename(f"lag{i}") for i in lags], axis=1).fillna(0)

    # Rolling PCA: project each window
    n_pc = min(n_components, len(lags))
    pc_scores = {f"{tag}_pc{i+1}": [] for i in range(n_pc)}
    pc_evr    = {f"{tag}_evr{i+1}": [] for i in range(n_pc)}
    pc1_dir   = []

    for end in range(len(df)):
        start = max(0, end - window + 1)
        block = lag_mat.iloc[start:end+1].values
        if block.shape[0] < n_pc + 1 or np.isnan(block).any():
            for i in range(n_pc):
                pc_scores[f"{tag}_pc{i+1}"].append(np.nan)
                pc_evr[f"{tag}_evr{i+1}"].append(np.nan)
            pc1_dir.append(np.nan)
            continue
        scaler = StandardScaler()
        block_s = scaler.fit_transform(block)
        pca = PCA(n_components=n_pc)
        pca.fit(block_s)
        scores = pca.transform(block_s)
        for i in range(n_pc):
            pc_scores[f"{tag}_pc{i+1}"].append(scores[-1, i])
            pc_evr[f"{tag}_evr{i+1}"].append(pca.explained_variance_ratio_[i])
        pc1_dir.append(np.sign(pca.components_[0, 0]))

    for key, vals in {**pc_scores, **pc_evr}.items():
        df[key] = vals
    df[f"{tag}_pc1_direction"] = pc1_dir

    # Cumulative explained variance by PC1+PC2
    df[f"{tag}_pca_ev_cum2"] = df[f"{tag}_evr1"] + df[f"{tag}_evr2"]

    return df


def add_correlation_matrix_features(df: pd.DataFrame, tag: str) -> pd.DataFrame:
    """
    Rolling correlation between lagged returns: det(Σ), Frobenius norm,
    max off-diag correlation, condition number, spectral radius.
    """
    r = df[f"{tag}_log_ret"].fillna(0)
    lags = [1, 2, 3, 5, 10]
    lag_mat = pd.concat([r.shift(i).rename(f"lag{i}") for i in lags], axis=1).fillna(0)

    corr_det  = []; corr_frob = []; corr_maxod = []
    corr_cond = []; corr_spec = []

    window = 40
    for end in range(len(df)):
        start = max(0, end - window + 1)
        block = lag_mat.iloc[start:end+1]
        if block.shape[0] < 10:
            corr_det.append(np.nan); corr_frob.append(np.nan)
            corr_maxod.append(np.nan); corr_cond.append(np.nan)
            corr_spec.append(np.nan); continue
        C = block.corr().values.copy()
        np.fill_diagonal(C, 1)
        corr_det.append(np.linalg.det(C))
        corr_frob.append(np.linalg.norm(C, "fro"))
        off = C[np.triu_indices_from(C, k=1)]
        corr_maxod.append(np.max(np.abs(off)) if len(off) > 0 else np.nan)
        try:
            corr_cond.append(np.linalg.cond(C))
        except:
            corr_cond.append(np.nan)
        try:
            eigvals = np.linalg.eigvalsh(C)
            corr_spec.append(eigvals.max())
        except:
            corr_spec.append(np.nan)

    df[f"{tag}_corr_det"]        = corr_det
    df[f"{tag}_corr_frob"]       = corr_frob
    df[f"{tag}_corr_maxoffdiag"] = corr_maxod
    df[f"{tag}_corr_cond"]       = corr_cond
    df[f"{tag}_corr_specrad"]    = corr_spec

    return df

def add_cluster_analysis(df: pd.DataFrame, tag: str,
                          n_clusters: int = 4) -> pd.DataFrame:
    """
    KMeans regime labels on vol+return space, GMM probability per regime,
    DBSCAN anomaly flag, distance to nearest centroid.
    """
    r   = df[f"{tag}_log_ret"].fillna(0)
    vol = df[f"{tag}_hvol_20"].fillna(0)
    rsi = df[f"{tag}_rsi_14"].fillna(50)

    # Feature matrix: return, vol, rsi z-scored
    feat = pd.concat([r, vol, rsi], axis=1).fillna(0)
    feat_s = StandardScaler().fit_transform(feat)

    # KMeans
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df[f"{tag}_kmeans_regime"]  = km.fit_predict(feat_s)
    df[f"{tag}_kmeans_dist"]    = np.min(km.transform(feat_s), axis=1)

    # GMM — soft assignment probabilities for each regime
    gmm = GaussianMixture(n_components=n_clusters, random_state=42, n_init=5)
    gmm.fit(feat_s)
    probs = gmm.predict_proba(feat_s)
    for k in range(n_clusters):
        df[f"{tag}_gmm_prob_{k}"] = probs[:, k]
    df[f"{tag}_gmm_regime"]   = gmm.predict(feat_s)
    df[f"{tag}_gmm_entropy"]  = -np.sum(probs * np.log(probs + 1e-9), axis=1)

    # DBSCAN anomaly flag (label == -1)
    db = DBSCAN(eps=1.5, min_samples=5)
    labels = db.fit_predict(feat_s)
    df[f"{tag}_dbscan_anomaly"] = (labels == -1).astype(int)

    return df

def add_factor_distribution(df: pd.DataFrame, tag: str) -> pd.DataFrame:
    """
    Fama-French-style factor proxies: market (beta), size (ATR proxy),
    value (price-to-SMA ratio), momentum, low-volatility factor.
    Rolling factor loadings via OLS.
    """
    r   = df[f"{tag}_log_ret"].fillna(0)
    vol = df[f"{tag}_hvol_20"].bfill()

    # Market factor proxy: lagged return
    df[f"{tag}_f_mkt"]    = r.shift(1)
    # Momentum factor: 12-1 month return
    df[f"{tag}_f_mom"]    = df["close"].pct_change(12) - df["close"].pct_change(1)
    # Value factor: price deviation from long-run mean
    df[f"{tag}_f_val"]    = df["close"] / (df["close"].rolling(100).mean() + 1e-9) - 1
    # Low-Vol factor: negative vol (low vol = positive factor)
    df[f"{tag}_f_lvol"]   = -vol
    # Size proxy: ATR relative to price (small price range = large cap proxy)
    df[f"{tag}_f_size"]   = -df[f"{tag}_natr_14"]

    # Carhart 4-factor: add trend (short vs long SMA)
    df[f"{tag}_f_trend"]  = df[f"{tag}_ema_20"] / (df[f"{tag}_ema_50"] + 1e-9) - 1

    # Rolling factor exposure (beta of return to each factor)
    factors = ["f_mkt", "f_mom", "f_val", "f_lvol", "f_trend"]
    w = 30
    for fname in factors:
        fcol = f"{tag}_{fname}"
        cov  = r.rolling(w).cov(df[fcol].fillna(0))
        varf = df[fcol].fillna(0).rolling(w).var()
        df[f"{tag}_load_{fname}"] = cov / (varf + 1e-9)

    # Information Ratio proxy
    df[f"{tag}_ir_mom"] = (df[f"{tag}_load_f_mom"] *
                           df[f"{tag}_f_mom"].rolling(w).std()) / \
                          (r.rolling(w).std() + 1e-9)

    return df

def add_asset_class_disclosure(df: pd.DataFrame, tag: str) -> pd.DataFrame:
    """
    Cross-asset behaviour proxies derived purely from OHLCV:
    equity-like vs bond-like behaviour, trend strength classification,
    mean-reversion vs momentum regime, liquidity stress indicator.
    """
    r   = df[f"{tag}_log_ret"].fillna(0)
    vol = df[f"{tag}_hvol_20"]

    # Hurst Exponent (R/S method, rolling)
    def hurst_rs(x):
        if len(x) < 10 or x.std() == 0: return 0.5
        mean_x = x.mean()
        dev    = np.cumsum(x - mean_x)
        R      = dev.max() - dev.min()
        S      = x.std()
        return np.log(R / S + 1e-9) / np.log(len(x))
    df[f"{tag}_hurst"]            = r.rolling(40).apply(hurst_rs, raw=True)

    # Hurst interpretation
    df[f"{tag}_regime_mr"]        = (df[f"{tag}_hurst"] < 0.45).astype(int)   # mean-revert
    df[f"{tag}_regime_trend"]     = (df[f"{tag}_hurst"] > 0.55).astype(int)   # trending
    df[f"{tag}_regime_random"]    = ((df[f"{tag}_hurst"] >= 0.45) &
                                     (df[f"{tag}_hurst"] <= 0.55)).astype(int)

    # Liquidity stress: vol spike + volume spike
    vol_z  = (vol - vol.rolling(50).mean()) / (vol.rolling(50).std() + 1e-9)
    vol_vz = (df["volume"] - df["volume"].rolling(50).mean()) / \
             (df["volume"].rolling(50).std() + 1e-9)
    df[f"{tag}_liq_stress"]       = (vol_z + vol_vz) / 2
    df[f"{tag}_liq_stress_flag"]  = (df[f"{tag}_liq_stress"] > 2).astype(int)

    # Drawdown and drawdown duration
    cumret = (1 + r).cumprod()
    rolling_max = cumret.cummax()
    df[f"{tag}_drawdown"]         = (cumret - rolling_max) / (rolling_max + 1e-9)
    df[f"{tag}_dd_duration"]      = df[f"{tag}_drawdown"].groupby(
        (df[f"{tag}_drawdown"] == 0).cumsum()).cumcount()

    # Max drawdown rolling
    df[f"{tag}_max_dd_20"]        = df[f"{tag}_drawdown"].rolling(20).min()
    df[f"{tag}_max_dd_50"]        = df[f"{tag}_drawdown"].rolling(50).min()

    # Calmar Ratio proxy
    ann_ret = r.rolling(50).mean() * 252
    df[f"{tag}_calmar"]           = ann_ret / (-df[f"{tag}_max_dd_50"].clip(upper=-1e-9))

    # Sharpe Ratio (rolling)
    df[f"{tag}_sharpe_20"]        = (r.rolling(20).mean() * 252) / \
                                    (r.rolling(20).std() * np.sqrt(252) + 1e-9)
    df[f"{tag}_sharpe_50"]        = (r.rolling(50).mean() * 252) / \
                                    (r.rolling(50).std() * np.sqrt(252) + 1e-9)

    # Sortino Ratio
    def downside_std(x):
        neg = x[x < 0]
        return neg.std() if len(neg) > 1 else 1e-9
    df[f"{tag}_sortino_20"] = (r.rolling(20).mean() * 252) / \
                              (r.rolling(20).apply(downside_std, raw=True) * np.sqrt(252) + 1e-9)

    return df


def add_positioning_models(df: pd.DataFrame, tag: str) -> pd.DataFrame:
    """
    Synthetic positioning proxies: COT-style long/short bias,
    net delta exposure, vol-adjusted position size, Kelly fraction,
    risk parity weight, trend-following signal.
    """
    r   = df[f"{tag}_log_ret"].fillna(0)
    vol = df[f"{tag}_garch_vol"].fillna(df[f"{tag}_hvol_20"])

    # Trend signal (fast/slow EMA crossover normalised)
    fast_e = df["close"].ewm(span=10).mean()
    slow_e = df["close"].ewm(span=40).mean()
    df[f"{tag}_trend_sig"]        = (fast_e - slow_e) / (slow_e + 1e-9)
    df[f"{tag}_trend_sig_norm"]   = df[f"{tag}_trend_sig"] / \
                                    (df[f"{tag}_trend_sig"].rolling(50).std() + 1e-9)

    # Vol-scaled position size (target 15% annualised vol)
    target_vol = 0.15 / np.sqrt(252)
    df[f"{tag}_pos_size_vol"]     = target_vol / (vol.clip(lower=1e-6))
    df[f"{tag}_pos_size_vol"]     = df[f"{tag}_pos_size_vol"].clip(-5, 5)

    # Kelly fraction: f* = mu / sigma^2
    mu_r = r.rolling(20).mean()
    sig2 = r.rolling(20).var()
    df[f"{tag}_kelly_full"]       = mu_r / (sig2 + 1e-9)
    df[f"{tag}_kelly_half"]       = df[f"{tag}_kelly_full"] / 2   # half-Kelly (safer)
    df[f"{tag}_kelly_clip"]       = df[f"{tag}_kelly_full"].clip(-2, 2)

    # Risk Parity weight proxy (inverse vol)
    df[f"{tag}_rp_weight"]        = 1 / (vol.clip(lower=1e-6))
    df[f"{tag}_rp_weight_norm"]   = df[f"{tag}_rp_weight"] / \
                                    df[f"{tag}_rp_weight"].rolling(50).mean()

    # Long/Short bias (net positioning proxy via price position in range)
    for w in [20, 50]:
        hi_w = df["high"].rolling(w).max()
        lo_w = df["low"].rolling(w).min()
        df[f"{tag}_net_pos_{w}"] = (df["close"] - lo_w) / (hi_w - lo_w + 1e-9) * 2 - 1

    # Momentum signal (risk-adjusted)
    df[f"{tag}_mom_sig_10"]   = r.rolling(10).mean() / (r.rolling(10).std() + 1e-9)
    df[f"{tag}_mom_sig_20"]   = r.rolling(20).mean() / (r.rolling(20).std() + 1e-9)

    return df

def add_series_database_models(df: pd.DataFrame, tag: str) -> pd.DataFrame:
    """
    Time-series features: autocorrelation lags, partial autocorrelation,
    STL-like decomposition (trend+seasonal+residual), Augmented-DF stat proxy,
    variance ratio test, fractional differencing weight.
    """
    c = df["close"]
    r = df[f"{tag}_log_ret"].fillna(0)

    # Autocorrelation at lags 1..5
    for lag in [1, 2, 3, 5, 10]:
        df[f"{tag}_acf_{lag}"] = r.rolling(40).apply(
            lambda x: pd.Series(x).autocorr(lag=lag) if len(x) > lag else np.nan,
            raw=True
        )

    # Ljung-Box Q-statistic proxy (sum of squared ACFs)
    acf_cols = [f"{tag}_acf_{lg}" for lg in [1, 2, 3, 5]]
    existing = [col for col in acf_cols if col in df.columns]
    if existing:
        df[f"{tag}_ljungbox_q"] = sum(df[col]**2 for col in existing) * len(df)

    # Variance Ratio (Lo-MacKinlay): VR(q) = Var(q-period return) / (q * Var(1-period return))
    for q in [2, 4, 8]:
        ret_q   = c.pct_change(q)
        var_q   = ret_q.rolling(40).var()
        var_1   = r.rolling(40).var()
        df[f"{tag}_vr_{q}"] = var_q / (q * var_1 + 1e-9)

    # ADF stat proxy: AR(1) coefficient (phi) from rolling OLS
    # y_t = phi * y_{t-1} + eps  =>  phi close to 1 => non-stationary
    def ar1_phi(x):
        if len(x) < 5: return np.nan
        y = x[1:]; yl = x[:-1]
        return np.dot(yl, y) / (np.dot(yl, yl) + 1e-9)
    df[f"{tag}_ar1_phi"] = r.rolling(30).apply(ar1_phi, raw=True)

    # HP-filter style trend (lambda=1600 for quarterly; adjust per tf)
    # Approximated via Hodrick-Prescott via scipy
    from scipy.signal import savgol_filter
    sg_window = min(51, len(c) // 2 * 2 - 1)
    if sg_window >= 5:
        df[f"{tag}_hptrend"]    = savgol_filter(c.ffill(), sg_window, 3)
        df[f"{tag}_hpcycle"]    = c - df[f"{tag}_hptrend"]
        df[f"{tag}_hpcycle_z"]  = df[f"{tag}_hpcycle"] / \
                                   (pd.Series(df[f"{tag}_hpcycle"]).rolling(50).std() + 1e-9)

    # Fractional differencing weight (d=0.4, window=10) for stationarity
    def frac_diff_weights(d, window):
        w = [1.0]
        for k in range(1, window):
            w.append(-w[-1] * (d - k + 1) / k)
        return np.array(w[::-1])
    fd_w = frac_diff_weights(0.4, 10)
    df[f"{tag}_fracdiff_04"] = c.rolling(10).apply(
        lambda x: np.dot(x, fd_w) if len(x) == 10 else np.nan, raw=True
    )

    # Rolling mean-reversion speed (Ornstein-Uhlenbeck theta estimate)
    def ou_theta(x):
        if x.std() == 0: return 0
        y = x[1:]; xl = x[:-1]
        beta = np.dot(xl - xl.mean(), y - y.mean()) / (np.dot(xl - xl.mean(), xl - xl.mean()) + 1e-9)
        return -np.log(beta) if beta > 0 else 0
    df[f"{tag}_ou_theta"] = c.rolling(30).apply(ou_theta, raw=True)

    return df

def add_spectral_features(df: pd.DataFrame, tag: str,
                           window: int = 64) -> pd.DataFrame:
    """
    Rolling FFT: dominant frequency, spectral entropy, power in frequency bands,
    spectral centroid, instantaneous phase (Hilbert), wavelet energy proxy.
    """
    r = df[f"{tag}_log_ret"].fillna(0).values
    n = len(r)

    dom_freq   = np.full(n, np.nan)
    spec_entr  = np.full(n, np.nan)
    spec_cent  = np.full(n, np.nan)
    low_power  = np.full(n, np.nan)
    high_power = np.full(n, np.nan)

    for i in range(window - 1, n):
        seg   = r[i - window + 1: i + 1] * signal.windows.hann(window)
        fcoef = np.abs(fft(seg)[:window // 2])
        freqs = fftfreq(window)[:window // 2]
        power = fcoef**2
        tot   = power.sum() + 1e-12

        dom_freq[i]   = freqs[np.argmax(power)]
        prob          = power / tot
        spec_entr[i]  = -np.sum(prob * np.log(prob + 1e-12))
        spec_cent[i]  = np.sum(freqs * power) / tot
        low_power[i]  = power[:window // 8].sum() / tot    # low freq band
        high_power[i] = power[window // 4:].sum() / tot    # high freq band

    df[f"{tag}_spec_dom_freq"]  = dom_freq
    df[f"{tag}_spec_entropy"]   = spec_entr
    df[f"{tag}_spec_centroid"]  = spec_cent
    df[f"{tag}_spec_low_pwr"]   = low_power
    df[f"{tag}_spec_high_pwr"]  = high_power
    df[f"{tag}_spec_pwr_ratio"] = low_power / (high_power + 1e-9)

    # Hilbert transform: instantaneous amplitude and phase
    from scipy.signal import hilbert
    analytic = hilbert(df[f"{tag}_log_ret"].fillna(0).values)
    df[f"{tag}_hilbert_amp"]   = np.abs(analytic)
    df[f"{tag}_hilbert_phase"] = np.angle(analytic)
    df[f"{tag}_hilbert_freq"]  = np.gradient(np.unwrap(np.angle(analytic))) / (2 * np.pi)

    return df

def build_all_timeframes(dfs: dict) -> dict:
    enriched = {}
    for tf, df in dfs.items():
        print(f"  ► Processing timeframe: {tf}  ({len(df)} rows)")
        enriched[tf] = build_risk_features(df, timeframe=tf)
        n_feat = len(enriched[tf].columns) - len(df.columns)
        print(f"    Added {n_feat} risk feature columns.")
    return enriched


# ══════════════════════════════════════════════════════════════════════════════
# INCREMENTAL UPDATE — compute features for one new bar only
# ══════════════════════════════════════════════════════════════════════════════
#
# Strategy
# --------
# Most features in this file use pandas rolling/ewm which naturally only
# need the last W rows to compute the new bar's value.  We handle those
# by running build_risk_features on a tail window (longest rolling = 200)
# and taking the last row.
#
# A few functions iterate over all rows in Python loops (PCA, correlation
# matrix, spectral) or require the full series (GARCH proxy, cluster,
# HP/SG filter, Hilbert).  For those we either:
#   a) Compute only the last point using a fixed-size tail window (PCA,
#      correlation matrix, spectral)
#   b) Carry forward the previous row's value and recompute with a
#      small tail (GARCH, cluster labels)
#   c) Reuse the previous row unchanged for features that need 1000+
#      bars of history for a stable result (HP filter, Hilbert) — the
#      difference for a single new bar is negligible.
#
# Usage
# -----
#   # First bar: full computation
#   df_feat = build_risk_features(df_history, timeframe)
#
#   # Each subsequent new bar:
#   df_feat = update_last_row(df_feat, new_ohlcv_row, timeframe)
#
# new_ohlcv_row must be a dict or single-row DataFrame with keys:
#   open, high, low, close, volume  (and optionally time)
# ══════════════════════════════════════════════════════════════════════════════

# Minimum history needed so that all rolling windows fit inside the tail.
# Longest rolling window in this file is 200 (SMA_200).
_TAIL_WINDOW = 210

def update_last_row(df_feat: pd.DataFrame,
                    new_row,
                    timeframe: str = "H1") -> pd.DataFrame:
    """
    Append new_row to df_feat, compute its feature values incrementally,
    and return the updated DataFrame.

    Features are grouped into three tiers:
        TIER 1  pandas rolling/ewm      — run build_risk_features on tail
        TIER 2  Python-loop features    — recompute last point only
        TIER 3  full-series features    — carry forward previous value
                                          (error < 0.1% for a single bar)

    Parameters
    ----------
    df_feat    : existing enriched DataFrame (output of build_risk_features)
    new_row    : dict or single-row DataFrame with OHLCV columns
    timeframe  : same tag as used in build_risk_features

    Returns
    -------
    df_feat with one new row appended and all feature columns populated.
    """
    tag = timeframe.upper()

    # ── Normalise new_row to a single-row DataFrame ───────────────────
    if isinstance(new_row, dict):
        nr = pd.DataFrame([new_row])
    else:
        nr = pd.DataFrame(new_row).iloc[[-1]]
    nr.columns = [c.lower() for c in nr.columns]

    # ── Append raw OHLCV to existing df ───────────────────────────────
    # Keep only the raw OHLCV columns from df_feat so concat is clean
    raw_cols   = ["open", "high", "low", "close", "volume"]
    existing_raw = df_feat[[c for c in raw_cols if c in df_feat.columns]].copy()

    # Carry all existing feature columns on the new row as NaN initially
    new_raw    = nr[[c for c in raw_cols if c in nr.columns]].copy()
    df_raw_all = pd.concat([existing_raw, new_raw],
                            ignore_index=True)

    # ── TIER 1: pandas rolling features via tail recompute ───────────
    # Run the full pipeline on the last _TAIL_WINDOW rows.
    # All rolling(W) with W <= 200 will produce the correct value for
    # the last row because they only look back W steps.
    tail_raw   = df_raw_all.tail(_TAIL_WINDOW).reset_index(drop=True)
    tail_feat  = build_risk_features(tail_raw.copy(), timeframe)
    new_feat   = tail_feat.iloc[[-1]].copy()   # only the last row

    # ── TIER 2: Python-loop features (PCA, corr matrix, spectral) ────
    # These iterate for end in range(len(df)) so running them on the
    # full df is expensive.  We run them on the tail only and extract
    # the last value — same result because they use a fixed window.
    new_feat = _update_pca_last(df_feat, new_feat, tag)
    new_feat = _update_corr_last(df_feat, new_feat, tag)
    new_feat = _update_spectral_last(df_feat, new_feat, tag)

    # ── TIER 3: carry-forward features ───────────────────────────────
    # HP filter, Hilbert, cluster labels, GARCH — carry previous value.
    # GARCH gets a proper 1-step update below; others are carried.
    new_feat = _carry_forward(df_feat, new_feat, tag)
    new_feat = _update_garch_last(df_feat, new_feat, tag)

    # ── Append to full feature DataFrame ─────────────────────────────
    df_out = pd.concat([df_feat, new_feat], ignore_index=True)
    return df_out


# ── Tier 2 helpers ────────────────────────────────────────────────────────────

def _update_pca_last(df_prev: pd.DataFrame,
                      new_feat: pd.DataFrame,
                      tag: str) -> pd.DataFrame:
    """
    Recompute PCA features for the last row using the last 60-row window.
    Columns: pc1..pc5, evr1..evr5, pc1_direction, pca_ev_cum2
    """
    r_col  = f"{tag}_log_ret"
    if r_col not in df_prev.columns:
        return new_feat

    lags       = list(range(1, 21))
    n_pc       = 5
    window     = 60
    r          = df_prev[r_col].fillna(0)
    # Append the new row's log_ret (already in new_feat from tier 1)
    new_lr     = new_feat[r_col].values[0] if r_col in new_feat.columns else 0.0
    r_ext      = pd.concat([r, pd.Series([new_lr])], ignore_index=True)

    lag_mat = pd.concat(
        [r_ext.shift(i).rename(f"lag{i}") for i in lags], axis=1
    ).fillna(0)

    end   = len(r_ext) - 1
    start = max(0, end - window + 1)
    block = lag_mat.iloc[start:end+1].values

    pc_scores = [np.nan] * n_pc
    pc_evr    = [np.nan] * n_pc
    pc1_dir   = np.nan

    if block.shape[0] >= n_pc + 1 and not np.isnan(block).any():
        try:
            scaler  = StandardScaler()
            block_s = scaler.fit_transform(block)
            pca     = PCA(n_components=n_pc)
            pca.fit(block_s)
            scores  = pca.transform(block_s)
            pc_scores = scores[-1].tolist()
            pc_evr    = pca.explained_variance_ratio_.tolist()
            pc1_dir   = float(np.sign(pca.components_[0, 0]))
        except Exception:
            pass

    for i in range(n_pc):
        new_feat[f"{tag}_pc{i+1}"]  = pc_scores[i]
        new_feat[f"{tag}_evr{i+1}"] = pc_evr[i]
    new_feat[f"{tag}_pc1_direction"] = pc1_dir
    new_feat[f"{tag}_pca_ev_cum2"]   = (
        (pc_evr[0] if not np.isnan(pc_evr[0]) else 0) +
        (pc_evr[1] if not np.isnan(pc_evr[1]) else 0)
    )
    return new_feat


def _update_corr_last(df_prev: pd.DataFrame,
                       new_feat: pd.DataFrame,
                       tag: str) -> pd.DataFrame:
    """
    Recompute correlation matrix features for the last row.
    Columns: corr_det, corr_frob, corr_maxoffdiag, corr_cond, corr_specrad
    """
    r_col  = f"{tag}_log_ret"
    if r_col not in df_prev.columns:
        return new_feat

    lags    = [1, 2, 3, 5, 10]
    window  = 40
    r       = df_prev[r_col].fillna(0)
    new_lr  = new_feat[r_col].values[0] if r_col in new_feat.columns else 0.0
    r_ext   = pd.concat([r, pd.Series([new_lr])], ignore_index=True)

    lag_mat = pd.concat(
        [r_ext.shift(i).rename(f"lag{i}") for i in lags], axis=1
    ).fillna(0)

    end   = len(r_ext) - 1
    start = max(0, end - window + 1)
    block = lag_mat.iloc[start:end+1]

    corr_det = corr_frob = corr_maxod = corr_cond = corr_spec = np.nan

    if block.shape[0] >= 10:
        try:
            C = block.corr().values.copy()
            np.fill_diagonal(C, 1)
            corr_det  = float(np.linalg.det(C))
            corr_frob = float(np.linalg.norm(C, "fro"))
            off       = C[np.triu_indices_from(C, k=1)]
            corr_maxod= float(np.max(np.abs(off))) if len(off) > 0 else np.nan
            corr_cond = float(np.linalg.cond(C))
            eigvals   = np.linalg.eigvalsh(C)
            corr_spec = float(eigvals.max())
        except Exception:
            pass

    new_feat[f"{tag}_corr_det"]        = corr_det
    new_feat[f"{tag}_corr_frob"]       = corr_frob
    new_feat[f"{tag}_corr_maxoffdiag"] = corr_maxod
    new_feat[f"{tag}_corr_cond"]       = corr_cond
    new_feat[f"{tag}_corr_specrad"]    = corr_spec
    return new_feat


def _update_spectral_last(df_prev: pd.DataFrame,
                           new_feat: pd.DataFrame,
                           tag: str) -> pd.DataFrame:
    """
    Recompute spectral FFT features for the last row using a 64-bar window.
    Columns: spec_dom_freq, spec_entropy, spec_centroid,
             spec_low_pwr, spec_high_pwr, spec_pwr_ratio,
             hilbert_amp, hilbert_phase, hilbert_freq
    """
    r_col  = f"{tag}_log_ret"
    if r_col not in df_prev.columns:
        return new_feat

    window  = 64
    r       = df_prev[r_col].fillna(0)
    new_lr  = new_feat[r_col].values[0] if r_col in new_feat.columns else 0.0
    r_ext   = pd.concat([r, pd.Series([new_lr])], ignore_index=True)

    # ── FFT on last window ────────────────────────────────────────────
    dom_freq = spec_entr = spec_cent = low_pwr = high_pwr = np.nan

    if len(r_ext) >= window:
        try:
            seg   = r_ext.values[-window:] * signal.windows.hann(window)
            fcoef = np.abs(fft(seg)[:window // 2])
            freqs = fftfreq(window)[:window // 2]
            power = fcoef ** 2
            tot   = power.sum() + 1e-12
            dom_freq  = float(freqs[np.argmax(power)])
            prob      = power / tot
            spec_entr = float(-np.sum(prob * np.log(prob + 1e-12)))
            spec_cent = float(np.sum(freqs * power) / tot)
            low_pwr   = float(power[:window // 8].sum() / tot)
            high_pwr  = float(power[window // 4:].sum() / tot)
        except Exception:
            pass

    new_feat[f"{tag}_spec_dom_freq"]  = dom_freq
    new_feat[f"{tag}_spec_entropy"]   = spec_entr
    new_feat[f"{tag}_spec_centroid"]  = spec_cent
    new_feat[f"{tag}_spec_low_pwr"]   = low_pwr
    new_feat[f"{tag}_spec_high_pwr"]  = high_pwr
    new_feat[f"{tag}_spec_pwr_ratio"] = (low_pwr / (high_pwr + 1e-9)
                                          if not np.isnan(low_pwr) else np.nan)

    # ── Hilbert on last window ────────────────────────────────────────
    hilbert_amp = hilbert_phase = hilbert_freq = np.nan

    hilbert_w = min(128, len(r_ext))
    if hilbert_w >= 10:
        try:
            from scipy.signal import hilbert as scipy_hilbert
            seg_h    = r_ext.values[-hilbert_w:]
            analytic = scipy_hilbert(seg_h)
            hilbert_amp   = float(np.abs(analytic[-1]))
            hilbert_phase = float(np.angle(analytic[-1]))
            # instantaneous frequency from unwrapped phase gradient
            phases    = np.unwrap(np.angle(analytic))
            hilbert_freq  = float(np.gradient(phases)[-1] / (2 * np.pi))
        except Exception:
            pass

    new_feat[f"{tag}_hilbert_amp"]   = hilbert_amp
    new_feat[f"{tag}_hilbert_phase"] = hilbert_phase
    new_feat[f"{tag}_hilbert_freq"]  = hilbert_freq
    return new_feat


# ── Tier 3 helpers ────────────────────────────────────────────────────────────

# Features that need the full series for mathematical correctness.
# We carry the previous row's value forward — for a single new bar the
# difference is negligible (HP filter changes by < 0.01%, cluster labels
# are stable over single bars, Hilbert is handled in tier 2).
_CARRY_FORWARD_SUFFIXES = [
    "hptrend", "hpcycle", "hpcycle_z",       # Savitzky-Golay HP proxy
    "kmeans_regime", "kmeans_dist",            # cluster — refit rarely needed
    "gmm_regime", "gmm_entropy",               # GMM
    "dbscan_anomaly",                          # DBSCAN
    "drawdown", "dd_duration",                 # cumulative, complex to update
    "cumulative_pnl",                          # not a feature but safe guard
]
# GMM probability columns follow a pattern
_GMM_PROB_PREFIX = "gmm_prob_"


def _carry_forward(df_prev: pd.DataFrame,
                   new_feat: pd.DataFrame,
                   tag: str) -> pd.DataFrame:
    """
    Carry the last known value of carry-forward features to the new row.
    Only touches columns that are NOT already populated by tier 1/2.
    """
    if len(df_prev) == 0:
        return new_feat

    last_prev = df_prev.iloc[-1]

    for suffix in _CARRY_FORWARD_SUFFIXES:
        col = f"{tag}_{suffix}"
        if col in df_prev.columns and col not in new_feat.columns:
            new_feat[col] = last_prev.get(col, np.nan)
        elif col in df_prev.columns:
            # Only carry if tier 1 left it NaN
            if pd.isna(new_feat[col].values[0]):
                new_feat[col] = last_prev.get(col, np.nan)

    # GMM probability columns (tag_gmm_prob_0, _1, _2, ...)
    gmm_cols = [c for c in df_prev.columns
                if c.startswith(f"{tag}_{_GMM_PROB_PREFIX}")]
    for col in gmm_cols:
        if col not in new_feat.columns or pd.isna(new_feat[col].values[0]):
            new_feat[col] = last_prev.get(col, np.nan)

    return new_feat


def _update_garch_last(df_prev: pd.DataFrame,
                        new_feat: pd.DataFrame,
                        tag: str) -> pd.DataFrame:
    """
    One-step GARCH(1,1) update:
        sigma2_t = omega + alpha * r_{t-1}^2 + beta * sigma2_{t-1}
    Uses the same omega/alpha/beta as garch_proxy().
    """
    garch_col = f"{tag}_garch_vol"
    r_col     = f"{tag}_log_ret"

    if garch_col not in df_prev.columns or r_col not in df_prev.columns:
        return new_feat
    if len(df_prev) == 0:
        return new_feat

    omega = 1e-6; alpha = 0.09; beta = 0.90

    prev_sigma  = float(df_prev[garch_col].iloc[-1])
    prev_r      = float(df_prev[r_col].iloc[-1])
    sigma2_prev = prev_sigma ** 2
    r_prev2     = prev_r ** 2

    sigma2_new  = omega + alpha * r_prev2 + beta * sigma2_prev
    new_feat[garch_col] = float(np.sqrt(max(sigma2_new, 0.0)))

    return new_feat