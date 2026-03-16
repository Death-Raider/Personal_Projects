"""
QUANTRIX — Risk Model Dashboard Generator
==========================================
Generates a multi-section matplotlib dashboard covering all 270 feature columns
from build_risk_features(). Sections are logically grouped and clearly labelled.

Usage:
    from risk_dashboard import plot_risk_dashboard
    plot_risk_dashboard(df, tag="M5", save_path="dashboard_M5.png")
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.ticker import MaxNLocator
import matplotlib.cm as cm
import warnings
warnings.filterwarnings("ignore")

# ── Palette ────────────────────────────────────────────────────────────────
BG      = "#03060f"
SURFACE = "#0a101e"
SURF2   = "#0f1a2e"
BORDER  = "#1a2f50"
ACCENT  = "#00d4ff"
ACC2    = "#ff6b35"
ACC3    = "#7fff6b"
ACC4    = "#bf5fff"
WARN    = "#ffcc00"
DANGER  = "#ff3860"
LGREY   = "#4a6080"
TWHITE  = "#d0e4f7"
TMID    = "#7a9cbd"

CMAP_DIV  = LinearSegmentedColormap.from_list("qx_div",  ["#ff3860","#03060f","#00d4ff"])
CMAP_SEQ  = LinearSegmentedColormap.from_list("qx_seq",  ["#0a101e","#00d4ff","#7fff6b"])
CMAP_HEAT = LinearSegmentedColormap.from_list("qx_heat", ["#03060f","#bf5fff","#ffcc00","#ff6b35"])

def _style_ax(ax, title="", xlabel="", ylabel="", grid=True, fs=7):
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=TMID, labelsize=fs-1)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    if title:
        ax.set_title(title, color=TWHITE, fontsize=fs, fontweight="bold", pad=3)
    if xlabel:
        ax.set_xlabel(xlabel, color=TMID, fontsize=fs-1)
    if ylabel:
        ax.set_ylabel(ylabel, color=TMID, fontsize=fs-1)
    if grid:
        ax.grid(True, color=BORDER, linewidth=0.4, alpha=0.6)
    ax.set_xlim(left=0)

def _section_label(fig, x, y, text, fs=11):
    fig.text(x, y, text, color=ACCENT, fontsize=fs, fontweight="bold",
             fontfamily="monospace", transform=fig.transFigure)

def _safe(df, col):
    if col in df.columns:
        return df[col]
    return pd.Series(np.nan, index=df.index)

def _fill(ax, series, color, alpha=0.15):
    idx = np.arange(len(series))
    ax.fill_between(idx, series.fillna(0), 0, color=color, alpha=alpha)

def _line(ax, series, color=ACCENT, lw=0.8, label=None, alpha=1.0):
    ax.plot(series.values, color=color, lw=lw, label=label, alpha=alpha)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

def plot_risk_dashboard(df: pd.DataFrame, tag: str = "M5",
                        save_path: str = "risk_dashboard.png"):
    """
    Parameters
    ----------
    df        : enriched DataFrame output of build_risk_features()
    tag       : timeframe tag (e.g. "M5", "H1")
    save_path : output PNG path
    """
    T = tag
    n = len(df)
    idx = np.arange(n)

    plt.rcParams.update({
        "figure.facecolor": BG,
        "axes.facecolor":   SURFACE,
        "text.color":       TWHITE,
        "font.family":      "monospace",
        "axes.labelcolor":  TMID,
        "xtick.color":      TMID,
        "ytick.color":      TMID,
    })

    # ── Master figure — tall single column of sections ─────────────────────
    fig = plt.figure(figsize=(36, 130))
    fig.patch.set_facecolor(BG)

    # Title
    fig.text(0.5, 0.9985, f"QUANTRIX  ·  STATISTICAL RISK DASHBOARD  ·  [{T}]",
             ha="center", va="top", color=ACCENT, fontsize=20,
             fontweight="bold", fontfamily="monospace")
    fig.text(0.5, 0.9980, f"n = {n} bars  ·  270 feature columns across 14 model groups",
             ha="center", va="top", color=TMID, fontsize=9, fontfamily="monospace")

    # We'll use a big outer GridSpec with one row per section, then subdivide
    SECTIONS = 14
    outer = gridspec.GridSpec(SECTIONS, 1, figure=fig,
                              hspace=0.06,
                              top=0.997, bottom=0.001,
                              left=0.04, right=0.98)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 0 — PRICE & RETURNS
    # ══════════════════════════════════════════════════════════════════════
    sec = gridspec.GridSpecFromSubplotSpec(2, 4, subplot_spec=outer[0], hspace=0.45, wspace=0.3)
    _section_header(fig, outer[0], "§0  PRICE  ·  RETURNS  ·  OHLCV")

    # Price + SMAs
    ax = fig.add_subplot(sec[0, :2])
    _line(ax, df["close"], ACCENT, 0.9, "close")
    for col, col2, lw in [("sma_20","",""), ("sma_50","",""), ("ema_20","","")]:
        s = _safe(df, f"{T}_{col}")
        c2 = {"sma_20": ACC2, "sma_50": ACC3, "ema_20": ACC4}.get(col, TMID)
        _line(ax, s, c2, 0.7, col)
    ax.legend(fontsize=6, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE, ncol=4)
    _style_ax(ax, "Close Price + SMA20/50, EMA20")

    # Volume
    ax2 = fig.add_subplot(sec[1, :2])
    colors_v = [ACC3 if r >= 0 else DANGER for r in _safe(df, f"{T}_ret").fillna(0)]
    ax2.bar(idx, df["volume"].values, color=colors_v, width=1.0, alpha=0.7)
    vol_ma = _safe(df, f"{T}_vol_ma20")
    _line(ax2, vol_ma, WARN, 1.0, "vol_ma20")
    _style_ax(ax2, "Volume  (green=up, red=down)  + Vol MA20")

    # Log returns
    ax3 = fig.add_subplot(sec[0, 2])
    r_s = _safe(df, f"{T}_log_ret")
    _line(ax3, r_s, ACCENT, 0.6)
    _fill(ax3, r_s, ACCENT)
    _style_ax(ax3, "Log Return")

    # Multi-period returns
    ax4 = fig.add_subplot(sec[1, 2])
    for col, c2 in [(f"{T}_ret_5", ACC2), (f"{T}_ret_10", ACC3), (f"{T}_ret_20", ACC4)]:
        _line(ax4, _safe(df, col), c2, 0.7, col.split("_")[-1])
    ax4.legend(fontsize=6, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _style_ax(ax4, "Returns: 5/10/20 bar")

    # Cumulative return
    ax5 = fig.add_subplot(sec[0, 3])
    cr = _safe(df, f"{T}_cum_ret")
    _line(ax5, cr, ACC3, 1.0)
    _fill(ax5, cr, ACC3)
    _style_ax(ax5, "Cumulative Return")

    # VWAP vs close
    ax6 = fig.add_subplot(sec[1, 3])
    _line(ax6, df["close"], ACCENT, 0.8, "close")
    _line(ax6, _safe(df, f"{T}_vwap"), WARN, 0.8, "VWAP")
    ax6.legend(fontsize=6, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _style_ax(ax6, "Close vs VWAP")

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 1 — DISTRIBUTION HIGHER MOMENTS
    # ══════════════════════════════════════════════════════════════════════
    sec = gridspec.GridSpecFromSubplotSpec(3, 4, subplot_spec=outer[1], hspace=0.55, wspace=0.35)
    _section_header(fig, outer[1], "§1  DISTRIBUTION HIGHER MOMENTS")

    moment_defs = [
        ("mean",    "Mean",          ACCENT),
        ("std",     "Std Dev",       ACC2),
        ("skew",    "Skewness",      ACC3),
        ("kurt",    "Kurtosis (ex)", ACC4),
        ("moment5", "5th Moment",    WARN),
        ("moment6", "6th Moment",    DANGER),
        ("jb_stat", "Jarque-Bera",   "#ff9f43"),
        ("semi_var","Semi-Variance", "#54a0ff"),
        ("entropy", "Shannon Entropy","#5f27cd"),
    ]
    windows = [10, 20, 50]
    cmap_wins = {10: ACCENT, 20: ACC2, 50: ACC4}

    positions = [(r, c) for r in range(3) for c in range(4)][:9]
    for (row, col_), (mkey, mname, _) in zip(positions, moment_defs):
        ax = fig.add_subplot(sec[row, col_])
        for w in windows:
            s = _safe(df, f"{T}_m{w}_{mkey}")
            _line(ax, s, cmap_wins[w], 0.7, f"w{w}")
        if mkey in ("skew", "kurt", "moment5", "moment6"):
            ax.axhline(0, color=LGREY, lw=0.5, ls="--")
        ax.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
        _style_ax(ax, mname, fs=6)

    # Return distribution histogram (last 100 bars)
    ax_h = fig.add_subplot(sec[2, 3])
    r_vals = _safe(df, f"{T}_log_ret").dropna().values[-200:]
    ax_h.hist(r_vals, bins=40, color=ACCENT, alpha=0.7, edgecolor=BORDER, linewidth=0.3)
    mu, sig = r_vals.mean(), r_vals.std()
    x_n = np.linspace(r_vals.min(), r_vals.max(), 100)
    from scipy import stats
    ax_h.plot(x_n, stats.norm.pdf(x_n, mu, sig) * len(r_vals) * (r_vals.max()-r_vals.min())/40,
              color=WARN, lw=1.2, label="Normal fit")
    ax_h.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _style_ax(ax_h, "Return Distribution (tail=200)", grid=False)
    ax_h.set_xlim(left=None)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 2 — VaR MODELS
    # ══════════════════════════════════════════════════════════════════════
    sec = gridspec.GridSpecFromSubplotSpec(2, 4, subplot_spec=outer[2], hspace=0.5, wspace=0.32)
    _section_header(fig, outer[2], "§2  VALUE-AT-RISK  ·  CVaR  ·  EWMA")

    var_panels = [
        ("Historical VaR 95/99 (w20)",
         [f"{T}_w20_cl95_hvar", f"{T}_w20_cl99_hvar"],
         [ACC3, DANGER]),
        ("Historical CVaR 95/99 (w20)",
         [f"{T}_w20_cl95_hcvar", f"{T}_w20_cl99_hcvar"],
         [ACC3, DANGER]),
        ("Parametric Normal VaR (w20)",
         [f"{T}_w20_cl95_pvar_norm", f"{T}_w20_cl99_pvar_norm"],
         [ACCENT, ACC4]),
        ("Student-t VaR (w20 cl95/99)",
         [f"{T}_w20_cl95_tvar", f"{T}_w20_cl99_tvar"],
         [ACC2, WARN]),
        ("Cornish-Fisher VaR (w20/w50)",
         [f"{T}_w20_cl95_cfvar", f"{T}_w50_cl95_cfvar"],
         [ACC3, ACC4]),
        ("EWMA Vol (λ=0.94)",
         [f"{T}_ewma_vol_94"],
         [ACCENT]),
        ("EWMA VaR 95 / 99",
         [f"{T}_ewma_var_95", f"{T}_ewma_var_99"],
         [ACC3, DANGER]),
        ("Historical VaR w50 vs w20 (cl95)",
         [f"{T}_w20_cl95_hvar", f"{T}_w50_cl95_hvar"],
         [ACCENT, ACC2]),
    ]

    for i, (title, cols, colors) in enumerate(var_panels):
        r_, c_ = divmod(i, 4)
        ax = fig.add_subplot(sec[r_, c_])
        for col, col2 in zip(cols, colors):
            s = _safe(df, col)
            _line(ax, s, col2, 0.75, col.split("_cl")[0].split("_w")[-1] + "_" + col.split("_")[-1])
        ax.axhline(0, color=LGREY, lw=0.4, ls="--")
        ax.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
        _style_ax(ax, title, fs=6)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 3 — VOLATILITY MODELS
    # ══════════════════════════════════════════════════════════════════════
    sec = gridspec.GridSpecFromSubplotSpec(2, 4, subplot_spec=outer[3], hspace=0.5, wspace=0.32)
    _section_header(fig, outer[3], "§3  VOLATILITY MODELS  ·  GARCH  ·  ATR")

    vol_panels = [
        ("Historical Vol (5/10/20/50)",
         [f"{T}_hvol_5", f"{T}_hvol_10", f"{T}_hvol_20", f"{T}_hvol_50"],
         [ACCENT, ACC2, ACC3, ACC4]),
        ("Parkinson vs Garman-Klass (w20)",
         [f"{T}_pk_vol_20", f"{T}_gk_vol_20"],
         [ACC2, ACC3]),
        ("Rogers-Satchell vs Yang-Zhang",
         [f"{T}_rs_vol_20", f"{T}_yz_vol_20"],
         [ACC4, WARN]),
        ("GARCH(1,1) vs EWMA Vol",
         [f"{T}_garch_vol", f"{T}_ewma_vol_94"],
         [DANGER, ACCENT]),
        ("ATR (5/14/20)",
         [f"{T}_atr_5", f"{T}_atr_14", f"{T}_atr_20"],
         [ACCENT, ACC2, ACC4]),
        ("Normalised ATR (NATR)",
         [f"{T}_natr_14"],
         [ACC3]),
        ("Volatility Ratio (ATR/ATR_MA)",
         [f"{T}_vol_ratio"],
         [WARN]),
        ("Volatility of Volatility",
         [f"{T}_vol_of_vol"],
         [DANGER]),
    ]

    for i, (title, cols, colors) in enumerate(vol_panels):
        r_, c_ = divmod(i, 4)
        ax = fig.add_subplot(sec[r_, c_])
        for col, col2 in zip(cols, colors):
            lbl = col.replace(f"{T}_", "").replace("_", " ")
            _line(ax, _safe(df, col), col2, 0.75, lbl)
        ax.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
        _style_ax(ax, title, fs=6)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 4 — TECHNICAL ANALYSIS
    # ══════════════════════════════════════════════════════════════════════
    sec = gridspec.GridSpecFromSubplotSpec(4, 4, subplot_spec=outer[4], hspace=0.55, wspace=0.32)
    _section_header(fig, outer[4], "§4  TECHNICAL ANALYSIS  ·  MOMENTUM  ·  TREND  ·  VOLUME")

    ta_panels = [
        # Row 0
        ("MACD + Signal + Histogram",
         [(f"{T}_macd", ACCENT, 0.9), (f"{T}_macd_signal", WARN, 0.9),
          (f"{T}_macd_hist", ACC3, 0.6)], "bar_hist"),
        ("RSI 7 & 14",
         [(f"{T}_rsi_14", ACCENT, 0.9), (f"{T}_rsi_7", ACC2, 0.7)], "rsi"),
        ("Stochastic K/D",
         [(f"{T}_stoch_k_14", ACCENT, 0.8), (f"{T}_stoch_d_14", WARN, 0.9)], "stoch"),
        ("Williams %R",
         [(f"{T}_williams_r", ACC4, 0.8)], "williams"),
        # Row 1
        ("ROC 5/10/20",
         [(f"{T}_roc_5", ACCENT, 0.7), (f"{T}_roc_10", ACC2, 0.7),
          (f"{T}_roc_20", ACC4, 0.7)], "line"),
        ("CCI (20)",
         [(f"{T}_cci_20", ACC3, 0.8)], "cci"),
        ("ADX + PDI + MDI",
         [(f"{T}_adx", WARN, 1.0), (f"{T}_pdi", ACC3, 0.7),
          (f"{T}_mdi", DANGER, 0.7)], "adx"),
        ("Bollinger Band %",
         [(f"{T}_bb_pct", ACCENT, 0.8), (f"{T}_bb_width", ACC2, 0.7)], "line"),
        # Row 2
        ("Keltner Channel %",
         [(f"{T}_kc_pct", ACC4, 0.8)], "line"),
        ("BB Squeeze Signal",
         [(f"{T}_squeeze", ACC3, 0.9)], "step"),
        ("OBV",
         [(f"{T}_obv", ACCENT, 0.7)], "line"),
        ("CMF20 + MFI14",
         [(f"{T}_cmf_20", ACC3, 0.8), (f"{T}_mfi_14", WARN, 0.7)], "line"),
        # Row 3
        ("Price vs SMA20/50",
         [(f"{T}_price_vs_sma20", ACCENT, 0.8), (f"{T}_price_vs_sma50", ACC2, 0.8)], "line"),
        ("Ichimoku Cloud Width",
         [(f"{T}_cloud_width", ACC4, 0.8), (f"{T}_cloud_pos", WARN, 0.6)], "line"),
        ("Pivot R1/S1 distance",
         [(f"{T}_dist_to_r1", ACC3, 0.8), (f"{T}_dist_to_s1", DANGER, 0.8)], "line"),
        ("Tenkan / Kijun",
         [(f"{T}_tenkan", ACCENT, 0.8), (f"{T}_kijun", ACC2, 0.8)], "price"),
    ]

    for i, (title, series_list, mode) in enumerate(ta_panels):
        r_, c_ = divmod(i, 4)
        ax = fig.add_subplot(sec[r_, c_])
        for col, col2, lw in series_list:
            s = _safe(df, col)
            lbl = col.replace(f"{T}_", "")
            if mode == "bar_hist" and "hist" in col:
                pos_v = s.clip(lower=0); neg_v = s.clip(upper=0)
                ax.bar(idx, pos_v.values, color=ACC3, width=1, alpha=0.7)
                ax.bar(idx, neg_v.values, color=DANGER, width=1, alpha=0.7)
            elif mode == "step":
                ax.step(idx, s.fillna(0).values, color=col2, lw=lw, where="mid")
            else:
                _line(ax, s, col2, lw, lbl)
        if mode in ("rsi", "stoch"):
            ax.axhline(70, color=DANGER, lw=0.5, ls="--", alpha=0.7)
            ax.axhline(30, color=ACC3,   lw=0.5, ls="--", alpha=0.7)
        if mode == "cci":
            ax.axhline(100, color=DANGER, lw=0.5, ls="--", alpha=0.7)
            ax.axhline(-100, color=ACC3,  lw=0.5, ls="--", alpha=0.7)
        ax.axhline(0, color=LGREY, lw=0.4, ls="--")
        ax.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
        _style_ax(ax, title, fs=6)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 5 — REGRESSION MODELS
    # ══════════════════════════════════════════════════════════════════════
    sec = gridspec.GridSpecFromSubplotSpec(2, 4, subplot_spec=outer[5], hspace=0.5, wspace=0.32)
    _section_header(fig, outer[5], "§5  REGRESSION MODELS  ·  OLS  ·  BETA  ·  ALPHA")

    reg_panels = [
        ("OLS Slope (w20 / w50)",
         [f"{T}_reg20_slope_norm", f"{T}_reg50_slope_norm"],
         [ACCENT, ACC2], True),
        ("R² Quality (w20 / w50)",
         [f"{T}_reg20_r2", f"{T}_reg50_r2"],
         [ACC3, ACC4], False),
        ("OLS Residual (w20 / w50)",
         [f"{T}_reg20_residual", f"{T}_reg50_residual"],
         [ACC2, WARN], True),
        ("1-Bar Forecast vs Close",
         [f"{T}_reg20_forecast1"],
         [DANGER], False),
        ("Quadratic Curvature (w20/w50)",
         [f"{T}_reg20_quad_curv", f"{T}_reg50_quad_curv"],
         [ACC4, ACCENT], True),
        ("Rolling Beta (w20 / w50)",
         [f"{T}_reg20_beta", f"{T}_reg50_beta"],
         [ACC3, WARN], True),
        ("Rolling Alpha (w20 / w50)",
         [f"{T}_reg20_alpha", f"{T}_reg50_alpha"],
         [ACC2, DANGER], True),
        ("Forecast vs Actual overlay",
         [f"{T}_reg50_forecast1"],
         [ACC3], False),
    ]

    for i, (title, cols, colors, zero_line) in enumerate(reg_panels):
        r_, c_ = divmod(i, 4)
        ax = fig.add_subplot(sec[r_, c_])
        for col, col2 in zip(cols, colors):
            lbl = col.replace(f"{T}_", "")
            if "forecast" in col and i == 7:
                _line(ax, df["close"], LGREY, 0.6, "close")
            _line(ax, _safe(df, col), col2, 0.75, lbl)
        if zero_line:
            ax.axhline(0, color=LGREY, lw=0.4, ls="--")
        ax.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
        _style_ax(ax, title, fs=6)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 6 — LAPLACE & TAYLOR TRANSFORMS
    # ══════════════════════════════════════════════════════════════════════
    sec = gridspec.GridSpecFromSubplotSpec(2, 4, subplot_spec=outer[6], hspace=0.5, wspace=0.32)
    _section_header(fig, outer[6], "§6  LAPLACE TRANSFORMS  ·  TAYLOR SERIES  ·  CUMULANTS")

    laplace_panels = [
        ("Taylor Orders 1–4 (w20)",
         [f"{T}_taylor_t1_20", f"{T}_taylor_t2_20",
          f"{T}_taylor_t3_20", f"{T}_taylor_t4_20"],
         [ACCENT, ACC2, ACC3, ACC4]),
        ("Taylor Sum (4th order)",
         [f"{T}_taylor_sum4_20"],
         [WARN]),
        ("Moment Generating Function",
         [f"{T}_mgf_t0p5", f"{T}_mgf_t1p0", f"{T}_mgf_t2p0"],
         [ACC3, ACCENT, DANGER]),
        ("Laplace s=0.1 / s=0.5",
         [f"{T}_laplace_s0p1", f"{T}_laplace_s0p5"],
         [ACCENT, ACC4]),
        ("Cumulant Gen. Function (CGF)",
         [f"{T}_cgf_t1"],
         [ACC2]),
        ("Cumulants κ1 / κ2",
         [f"{T}_kappa1_20", f"{T}_kappa2_20"],
         [ACCENT, ACC3]),
        ("Cumulants κ3 / κ4",
         [f"{T}_kappa3_20", f"{T}_kappa4_20"],
         [ACC4, WARN]),
        ("Exponential Smoothing (0.1/0.3/0.7)",
         [f"{T}_exp_smooth_0p1", f"{T}_exp_smooth_0p3", f"{T}_exp_smooth_0p7"],
         [ACCENT, ACC2, ACC4]),
    ]

    for i, (title, cols, colors) in enumerate(laplace_panels):
        r_, c_ = divmod(i, 4)
        ax = fig.add_subplot(sec[r_, c_])
        for col, col2 in zip(cols, colors):
            lbl = col.replace(f"{T}_", "")
            _line(ax, _safe(df, col), col2, 0.75, lbl)
        ax.axhline(0, color=LGREY, lw=0.4, ls="--")
        ax.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
        _style_ax(ax, title, fs=6)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 7 — PCA & CORRELATION MATRIX
    # ══════════════════════════════════════════════════════════════════════
    sec = gridspec.GridSpecFromSubplotSpec(2, 4, subplot_spec=outer[7], hspace=0.5, wspace=0.32)
    _section_header(fig, outer[7], "§7  PCA  ·  CORRELATION MATRIX  ·  EIGENSTRUCTURE")

    # PC1–PC5 scores
    ax = fig.add_subplot(sec[0, :2])
    pc_colors = [ACCENT, ACC2, ACC3, ACC4, WARN]
    for i in range(1, 6):
        s = _safe(df, f"{T}_pc{i}")
        _line(ax, s, pc_colors[i-1], 0.7, f"PC{i}")
    ax.axhline(0, color=LGREY, lw=0.4, ls="--")
    ax.legend(fontsize=6, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE, ncol=5)
    _style_ax(ax, "PCA Scores: PC1 – PC5")

    # Explained Variance Ratios
    ax2 = fig.add_subplot(sec[0, 2])
    for i in range(1, 6):
        s = _safe(df, f"{T}_evr{i}")
        _line(ax2, s, pc_colors[i-1], 0.7, f"EVR{i}")
    _line(ax2, _safe(df, f"{T}_pca_ev_cum2"), WARN, 1.0, "EVR1+2")
    ax2.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _style_ax(ax2, "Explained Variance Ratio")

    # PC1 direction
    ax3 = fig.add_subplot(sec[0, 3])
    s = _safe(df, f"{T}_pc1_direction")
    ax3.step(idx, s.fillna(0).values, color=ACC3, where="mid", lw=0.8)
    _fill(ax3, s, ACC3, 0.2)
    _style_ax(ax3, "PC1 Direction (+1 / -1)")

    # Correlation matrix heatmap (last available)
    ax4 = fig.add_subplot(sec[1, :2])
    corr_cols = [f"{T}_corr_det", f"{T}_corr_frob",
                 f"{T}_corr_maxoffdiag", f"{T}_corr_cond", f"{T}_corr_specrad"]
    for col, col2 in zip(corr_cols, [ACCENT, ACC2, ACC3, WARN, DANGER]):
        lbl = col.replace(f"{T}_corr_", "")
        s = _safe(df, col)
        _line(ax4, s / (s.rolling(50).max().clip(lower=1e-9)), col2, 0.75, lbl)
    ax4.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE, ncol=5)
    _style_ax(ax4, "Correlation Matrix Stats (normalised)")

    # Corr det / cond individually
    for i_, (col, col2, title) in enumerate([
        (f"{T}_corr_det",  ACC3, "Corr Matrix Det"),
        (f"{T}_corr_cond", WARN, "Corr Condition #"),
    ]):
        ax_ = fig.add_subplot(sec[1, 2 + i_])
        s = _safe(df, col)
        _line(ax_, s, col2, 0.8)
        _fill(ax_, s, col2, 0.15)
        _style_ax(ax_, title, fs=6)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 8 — CLUSTER ANALYSIS
    # ══════════════════════════════════════════════════════════════════════
    sec = gridspec.GridSpecFromSubplotSpec(2, 4, subplot_spec=outer[8], hspace=0.5, wspace=0.32)
    _section_header(fig, outer[8], "§8  CLUSTER ANALYSIS  ·  KMeans  ·  GMM  ·  DBSCAN")

    # KMeans regime coloured price
    ax = fig.add_subplot(sec[0, :2])
    regime = _safe(df, f"{T}_kmeans_regime").fillna(0).astype(int).values
    reg_colors = [ACCENT, ACC2, ACC3, ACC4, WARN]
    for k in range(4):
        mask = regime == k
        if mask.any():
            ax.fill_between(idx, df["close"].values, df["close"].min(),
                            where=mask, alpha=0.25, color=reg_colors[k], label=f"R{k}")
    _line(ax, df["close"], TWHITE, 0.6)
    ax.legend(fontsize=6, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE, ncol=4)
    _style_ax(ax, "KMeans Regime Overlay on Price")

    # KMeans distance
    ax2 = fig.add_subplot(sec[0, 2])
    _line(ax2, _safe(df, f"{T}_kmeans_dist"), ACC2, 0.8)
    _fill(ax2, _safe(df, f"{T}_kmeans_dist"), ACC2)
    _style_ax(ax2, "KMeans Centroid Distance")

    # DBSCAN anomaly
    ax3 = fig.add_subplot(sec[0, 3])
    anom = _safe(df, f"{T}_dbscan_anomaly").fillna(0)
    ax3.fill_between(idx, anom.values, 0, color=DANGER, alpha=0.6, step="mid")
    ax3.step(idx, anom.values, color=DANGER, where="mid", lw=0.8)
    _style_ax(ax3, "DBSCAN Anomaly Flag (1=outlier)")

    # GMM probabilities
    ax4 = fig.add_subplot(sec[1, :2])
    for k in range(4):
        s = _safe(df, f"{T}_gmm_prob_{k}")
        _line(ax4, s, reg_colors[k], 0.7, f"GMM_p{k}")
    ax4.legend(fontsize=6, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE, ncol=4)
    _style_ax(ax4, "GMM Regime Probabilities (soft assignment)")

    # GMM entropy
    ax5 = fig.add_subplot(sec[1, 2])
    s = _safe(df, f"{T}_gmm_entropy")
    _line(ax5, s, WARN, 0.8)
    _fill(ax5, s, WARN)
    _style_ax(ax5, "GMM Entropy (regime uncertainty)")

    # GMM regime
    ax6 = fig.add_subplot(sec[1, 3])
    gmm_r = _safe(df, f"{T}_gmm_regime").fillna(0).astype(int).values
    ax6.scatter(idx, gmm_r, c=[reg_colors[v % 4] for v in gmm_r], s=2, alpha=0.8)
    _style_ax(ax6, "GMM Regime Label", grid=False)
    ax6.set_xlim(0, n)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 9 — FACTOR DISTRIBUTION
    # ══════════════════════════════════════════════════════════════════════
    sec = gridspec.GridSpecFromSubplotSpec(2, 4, subplot_spec=outer[9], hspace=0.5, wspace=0.32)
    _section_header(fig, outer[9], "§9  FACTOR DISTRIBUTION  ·  LOADINGS  ·  IR")

    factors = ["f_mkt", "f_mom", "f_val", "f_lvol", "f_trend"]
    f_colors = [ACCENT, ACC2, ACC3, ACC4, WARN]

    # All factors raw
    ax = fig.add_subplot(sec[0, :2])
    for f, col2 in zip(factors, f_colors):
        s = _safe(df, f"{T}_{f}")
        s_n = s / (s.rolling(50).std().clip(lower=1e-9))
        _line(ax, s_n, col2, 0.7, f)
    ax.axhline(0, color=LGREY, lw=0.4, ls="--")
    ax.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE, ncol=5)
    _style_ax(ax, "Factor Signals (z-scored)")

    # All loadings
    ax2 = fig.add_subplot(sec[0, 2:])
    for f, col2 in zip(factors, f_colors):
        s = _safe(df, f"{T}_load_{f}")
        _line(ax2, s, col2, 0.7, f"β_{f}")
    ax2.axhline(0, color=LGREY, lw=0.4, ls="--")
    ax2.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE, ncol=5)
    _style_ax(ax2, "Factor Loadings (rolling OLS β)")

    # Individual factor panels
    factor_detail = [
        ("Momentum Factor + Loading",  "f_mom",   "load_f_mom"),
        ("Value Factor + Loading",     "f_val",   "load_f_val"),
        ("Low-Vol Factor + Loading",   "f_lvol",  "load_f_lvol"),
        ("Trend Factor + Loading",     "f_trend", "load_f_trend"),
    ]
    for i, (title, f_col, l_col) in enumerate(factor_detail):
        ax_ = fig.add_subplot(sec[1, i])
        s_f = _safe(df, f"{T}_{f_col}")
        s_l = _safe(df, f"{T}_{l_col}")
        _line(ax_, s_f / (s_f.rolling(50).std().clip(lower=1e-9)), f_colors[i], 0.8, "signal")
        ax_r = ax_.twinx()
        ax_r.plot(s_l.values, color=WARN, lw=0.7, alpha=0.8, label="loading")
        ax_r.tick_params(colors=TMID, labelsize=5)
        ax_r.spines["right"].set_edgecolor(BORDER)
        ax_.axhline(0, color=LGREY, lw=0.4, ls="--")
        _style_ax(ax_, title, fs=6)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 10 — ASSET CLASS DISCLOSURE
    # ══════════════════════════════════════════════════════════════════════
    sec = gridspec.GridSpecFromSubplotSpec(2, 4, subplot_spec=outer[10], hspace=0.5, wspace=0.32)
    _section_header(fig, outer[10], "§10  ASSET CLASS DISCLOSURE  ·  HURST  ·  DRAWDOWN  ·  RISK RATIOS")

    # Hurst + regime flags
    ax = fig.add_subplot(sec[0, :2])
    h_s = _safe(df, f"{T}_hurst")
    _line(ax, h_s, ACCENT, 0.9, "Hurst")
    ax.axhline(0.5, color=LGREY, lw=0.8, ls="--", label="H=0.5")
    ax.axhline(0.45, color=ACC3, lw=0.6, ls=":", alpha=0.7)
    ax.axhline(0.55, color=DANGER, lw=0.6, ls=":", alpha=0.7)
    ax.fill_between(idx, h_s.fillna(0.5).values, 0.5,
                    where=h_s.fillna(0.5).values > 0.55, color=DANGER, alpha=0.2, label="Trending")
    ax.fill_between(idx, h_s.fillna(0.5).values, 0.5,
                    where=h_s.fillna(0.5).values < 0.45, color=ACC3, alpha=0.2, label="Mean-Rev")
    ax.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _style_ax(ax, "Hurst Exponent  (>0.55 trend, <0.45 MR)")

    # Drawdown
    ax2 = fig.add_subplot(sec[0, 2])
    dd = _safe(df, f"{T}_drawdown")
    ax2.fill_between(idx, dd.values, 0, color=DANGER, alpha=0.5)
    _line(ax2, _safe(df, f"{T}_max_dd_20"), WARN, 0.8, "MaxDD20")
    _line(ax2, _safe(df, f"{T}_max_dd_50"), ACC4, 0.8, "MaxDD50")
    ax2.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _style_ax(ax2, "Drawdown + Max Drawdown")

    # DD Duration
    ax3 = fig.add_subplot(sec[0, 3])
    _line(ax3, _safe(df, f"{T}_dd_duration"), ACC2, 0.8)
    _fill(ax3, _safe(df, f"{T}_dd_duration"), ACC2)
    _style_ax(ax3, "Drawdown Duration (bars)")

    # Sharpe ratios
    ax4 = fig.add_subplot(sec[1, 0])
    _line(ax4, _safe(df, f"{T}_sharpe_20"), ACCENT, 0.8, "Sharpe20")
    _line(ax4, _safe(df, f"{T}_sharpe_50"), ACC2, 0.8, "Sharpe50")
    ax4.axhline(0, color=LGREY, lw=0.4, ls="--")
    ax4.axhline(1, color=ACC3, lw=0.5, ls=":", alpha=0.6)
    ax4.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _style_ax(ax4, "Rolling Sharpe Ratio", fs=6)

    # Sortino / Calmar
    ax5 = fig.add_subplot(sec[1, 1])
    _line(ax5, _safe(df, f"{T}_sortino_20"), ACC3, 0.8, "Sortino")
    _line(ax5, _safe(df, f"{T}_calmar").clip(-10, 10), WARN, 0.8, "Calmar")
    ax5.axhline(0, color=LGREY, lw=0.4, ls="--")
    ax5.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _style_ax(ax5, "Sortino / Calmar Ratio", fs=6)

    # Liquidity stress
    ax6 = fig.add_subplot(sec[1, 2])
    ls_s = _safe(df, f"{T}_liq_stress")
    _line(ax6, ls_s, WARN, 0.8)
    _fill(ax6, ls_s, WARN)
    ax6.axhline(2, color=DANGER, lw=0.6, ls="--", label="stress threshold")
    ax6.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _style_ax(ax6, "Liquidity Stress Index", fs=6)

    # Liq stress flag
    ax7 = fig.add_subplot(sec[1, 3])
    lsf = _safe(df, f"{T}_liq_stress_flag").fillna(0)
    ax7.fill_between(idx, lsf.values, 0, color=DANGER, alpha=0.6, step="mid")
    ax7.step(idx, lsf.values, color=DANGER, where="mid", lw=0.8)
    _style_ax(ax7, "Liquidity Stress Flag (>2σ)", fs=6)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 11 — POSITIONING MODELS
    # ══════════════════════════════════════════════════════════════════════
    sec = gridspec.GridSpecFromSubplotSpec(2, 4, subplot_spec=outer[11], hspace=0.5, wspace=0.32)
    _section_header(fig, outer[11], "§11  POSITIONING  ·  KELLY  ·  RISK PARITY  ·  SIGNALS")

    pos_panels = [
        ("Trend Signal (norm)",
         [f"{T}_trend_sig_norm"],
         [ACCENT], True),
        ("Vol-Scaled Position Size",
         [f"{T}_pos_size_vol"],
         [ACC2], False),
        ("Kelly Full / Half",
         [f"{T}_kelly_full", f"{T}_kelly_half", f"{T}_kelly_clip"],
         [DANGER, ACC2, ACC3], True),
        ("Risk Parity Weight (norm)",
         [f"{T}_rp_weight_norm"],
         [ACC4], False),
        ("Net Long/Short (w20/w50)",
         [f"{T}_net_pos_20", f"{T}_net_pos_50"],
         [ACCENT, ACC2], True),
        ("Momentum Signal (10/20)",
         [f"{T}_mom_sig_10", f"{T}_mom_sig_20"],
         [ACC3, WARN], True),
        ("IR Momentum",
         [f"{T}_ir_mom"],
         [ACC4], True),
        ("OBV + Trend overlay",
         [f"{T}_obv", f"{T}_trend_sig"],
         [ACCENT, ACC3], False),
    ]

    for i, (title, cols, colors, zero) in enumerate(pos_panels):
        r_, c_ = divmod(i, 4)
        ax = fig.add_subplot(sec[r_, c_])
        for col, col2 in zip(cols, colors):
            lbl = col.replace(f"{T}_", "")
            _line(ax, _safe(df, col), col2, 0.75, lbl)
        if zero:
            ax.axhline(0, color=LGREY, lw=0.4, ls="--")
        ax.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
        _style_ax(ax, title, fs=6)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 12 — TIME SERIES DATABASE MODELS
    # ══════════════════════════════════════════════════════════════════════
    sec = gridspec.GridSpecFromSubplotSpec(2, 4, subplot_spec=outer[12], hspace=0.5, wspace=0.32)
    _section_header(fig, outer[12], "§12  SERIES MODELS  ·  ACF  ·  STATIONARITY  ·  OU  ·  HP-FILTER")

    ts_panels = [
        ("ACF Lags 1/2/3/5/10",
         [f"{T}_acf_1", f"{T}_acf_2", f"{T}_acf_3", f"{T}_acf_5", f"{T}_acf_10"],
         [ACCENT, ACC2, ACC3, ACC4, WARN], True),
        ("Ljung-Box Q Statistic",
         [f"{T}_ljungbox_q"],
         [DANGER], False),
        ("Variance Ratio (q=2/4/8)",
         [f"{T}_vr_2", f"{T}_vr_4", f"{T}_vr_8"],
         [ACCENT, ACC2, ACC4], False),
        ("AR(1) Phi (unit root proxy)",
         [f"{T}_ar1_phi"],
         [ACC3], True),
        ("HP-Filter: Trend",
         [f"{T}_hptrend"],
         [ACCENT], False),
        ("HP-Filter: Cycle (z-scored)",
         [f"{T}_hpcycle_z"],
         [ACC2], True),
        ("Fractional Diff (d=0.4)",
         [f"{T}_fracdiff_04"],
         [ACC4], True),
        ("OU Mean-Reversion Speed θ",
         [f"{T}_ou_theta"],
         [WARN], False),
    ]

    for i, (title, cols, colors, zero) in enumerate(ts_panels):
        r_, c_ = divmod(i, 4)
        ax = fig.add_subplot(sec[r_, c_])
        for col, col2 in zip(cols, colors):
            lbl = col.replace(f"{T}_", "")
            _line(ax, _safe(df, col), col2, 0.75, lbl)
        if zero:
            ax.axhline(0, color=LGREY, lw=0.4, ls="--")
        if "vr" in title.lower():
            ax.axhline(1, color=LGREY, lw=0.6, ls="--", alpha=0.7)
        if "phi" in title.lower():
            ax.axhline(1, color=DANGER, lw=0.6, ls="--", alpha=0.7, label="unit root")
            ax.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
        ax.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
        _style_ax(ax, title, fs=6)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 13 — SPECTRAL ANALYSIS
    # ══════════════════════════════════════════════════════════════════════
    sec = gridspec.GridSpecFromSubplotSpec(2, 4, subplot_spec=outer[13], hspace=0.5, wspace=0.32)
    _section_header(fig, outer[13], "§13  SPECTRAL ANALYSIS  ·  FFT  ·  HILBERT  ·  POWER BANDS")

    spec_panels = [
        ("Dominant Frequency",
         [f"{T}_spec_dom_freq"],
         [ACCENT], False),
        ("Spectral Entropy",
         [f"{T}_spec_entropy"],
         [ACC2], False),
        ("Spectral Centroid",
         [f"{T}_spec_centroid"],
         [ACC3], True),
        ("Power: Low / High Band",
         [f"{T}_spec_low_pwr", f"{T}_spec_high_pwr"],
         [ACC4, DANGER], False),
        ("Low/High Power Ratio",
         [f"{T}_spec_pwr_ratio"],
         [WARN], False),
        ("Hilbert Amplitude",
         [f"{T}_hilbert_amp"],
         [ACCENT], False),
        ("Hilbert Phase",
         [f"{T}_hilbert_phase"],
         [ACC2], True),
        ("Hilbert Instantaneous Freq",
         [f"{T}_hilbert_freq"],
         [ACC4], True),
    ]

    for i, (title, cols, colors, zero) in enumerate(spec_panels):
        r_, c_ = divmod(i, 4)
        ax = fig.add_subplot(sec[r_, c_])
        for col, col2 in zip(cols, colors):
            lbl = col.replace(f"{T}_", "")
            s = _safe(df, col)
            _line(ax, s, col2, 0.75, lbl)
            if col2 == ACCENT:
                _fill(ax, s, col2, 0.12)
        if zero:
            ax.axhline(0, color=LGREY, lw=0.4, ls="--")
        ax.legend(fontsize=5, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
        _style_ax(ax, title, fs=6)

    # ── Finalise ────────────────────────────────────────────────────────────
    plt.savefig(save_path, dpi=130, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"✔ Dashboard saved → {save_path}")
    return save_path


# ── Helper: section header band ────────────────────────────────────────────

def _section_header(fig, subplot_spec, text):
    """Draws a coloured header bar at the top of each GridSpec section."""
    pos = subplot_spec.get_position(fig)
    # thin coloured rect across full width
    rect = mpatches.FancyBboxPatch(
        (pos.x0 - 0.005, pos.y1 - 0.0008),
        (pos.x1 - pos.x0 + 0.01), 0.0016,
        boxstyle="square,pad=0",
        linewidth=0, facecolor=ACCENT, alpha=0.18,
        transform=fig.transFigure, zorder=3, clip_on=False
    )
    fig.add_artist(rect)
    fig.text(pos.x0, pos.y1 + 0.0003, f"  {text}",
             color=ACCENT, fontsize=8.5, fontweight="bold",
             fontfamily="monospace", transform=fig.transFigure,
             va="bottom", zorder=4)

