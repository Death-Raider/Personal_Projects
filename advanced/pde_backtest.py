"""
PDE Backtest — Surface Recompute on Vol Regime Shift
=====================================================
1. Compute u(x, sigma) surface at start
2. Track current (x, sigma) path on the surface as dots
3. Recompute surface only when sigma_bar shifts by >= threshold
4. Each time TP or SL is hit → start new trade from that price
5. x is always bounded within [SL, TP] — never drifts to ±100
"""

import numpy as np
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

from plotting import *
from PDE_parameters import Params
from cfd_pde import solve_pde
from signal_gen import try_enter_trade

# ══════════════════════════════════════════════════════════════════════════════
# PARAMETER ESTIMATION — OHLCV ONLY, PRICE UNITS
# ══════════════════════════════════════════════════════════════════════════════

def estimate_params(df, w_sigma=20, w_bar=200,
                    w_eta=20, w_rho=60, w_beta=100):
    c       = df["close"]
    d_price = c.diff()

    sigma0    = d_price.rolling(w_sigma).std().iloc[-1]
    sigma_bar = d_price.rolling(w_bar).std().iloc[-1]

    vol_series = d_price.rolling(w_sigma).std()
    eta        = vol_series.diff().rolling(w_eta).std().iloc[-1]

    vc = vol_series.dropna().values[-w_beta:]
    if len(vc) >= 10:
        phi  = np.corrcoef(vc[:-1], vc[1:])[0, 1]
        phi  = np.clip(phi, 1e-6, 1 - 1e-6)
        beta = float(-np.log(phi))
    else:
        beta = 0.05

    d_vol = vol_series.diff()
    rho   = d_price.rolling(w_rho).corr(d_vol).iloc[-1]
    rho   = float(np.tanh(rho if not np.isnan(rho) else 0.0))

    return dict(
        sigma0    = max(float(sigma0),    1e-4),
        sigma_bar = max(float(sigma_bar), 1e-4),
        eta       = max(float(eta),       1e-4),
        beta      = max(float(beta),      1e-4),
        rho       = float(np.clip(rho, -0.99, 0.99)),
    )

class PDEBacktest:
    def __init__(self, p_base, mu_series, recompute_threshold=1.0):
        self.p_base    = p_base
        self.mu_series = mu_series
        self.threshold = recompute_threshold

        self.surfaces  = []   # PDE surfaces
        self.path      = []   # per-bar records
        self.trades    = []   # completed trade records
        self.regimes   = []   # bars where surface was recomputed

        self.last_sigma_bar     = None
        self.current_surface_id = -1

    def run(self, df, entry_price_col="close",
            w_sigma=20, w_bar=200):

        print(f"\n  Running PDE backtest over {len(df)} bars ...")
        print(f"  Recompute threshold : {self.threshold} pts")
        print(f"  TP={self.p_base.TP}  SL={self.p_base.SL}")

        vol_series  = df["close"].diff().rolling(w_sigma).std()
        sbar_series = df["close"].diff().rolling(w_bar).std()

        # ── Trade state ───────────────────────────────────────────────
        entry_price    = None       # None = no open trade
        trade_id       = 0
        trade_start    = w_bar
        cumulative_pnl = 0.0
        trade_open     = False
        trade_direction= "long"     # direction of current open trade

        for t in range(w_bar, len(df)):
            sigma_now = vol_series.iloc[t]
            sbar_now  = sbar_series.iloc[t]

            if np.isnan(sigma_now) or np.isnan(sbar_now):
                continue

            mu_now = float(self.mu_series[t]) \
                     if t < len(self.mu_series) else 0.0

            # ── Recompute surface if vol regime shifted ────────────────
            needs_recompute = (
                self.last_sigma_bar is None or
                abs(sbar_now - self.last_sigma_bar) >= self.threshold
            )

            if needs_recompute and t not in self.regimes:
                p_new           = Params()
                est             = estimate_params(df.iloc[:t+1],
                                                  w_sigma=w_sigma,
                                                  w_bar=w_bar)
                p_new.sigma0    = est["sigma0"]
                p_new.sigma_bar = est["sigma_bar"]
                p_new.eta       = est["eta"]
                p_new.beta      = est["beta"]
                p_new.rho       = est["rho"]
                p_new.TP        = self.p_base.TP
                p_new.SL        = self.p_base.SL
                p_new.r_kill    = self.p_base.r_kill
                p_new.Nx        = self.p_base.Nx
                p_new.Ns        = self.p_base.Ns
                p_new.sigma_max = max(p_new.sigma_bar * 4,
                                      p_new.sigma0    * 4, 8.0)

                print(f"  Bar {t:>5}  |  Recomputing  "
                      f"sbar={sbar_now:.3f}  "
                      f"shift={abs(sbar_now-(self.last_sigma_bar or sbar_now)):.3f}")

                u, x_grid, s_grid = solve_pde(p_new, mu=mu_now)
                self.current_surface_id += 1
                self.surfaces.append(dict(
                    bar       = t,
                    u         = u,
                    x_grid    = x_grid,
                    s_grid    = s_grid,
                    p         = p_new,
                    mu        = mu_now,
                    sigma_bar = sbar_now,
                ))
                self.regimes.append(t)
                self.last_sigma_bar = sbar_now

            # ── No surface yet — skip ──────────────────────────────────
            if self.current_surface_id < 0:
                continue

            surf = self.surfaces[self.current_surface_id]

            # ── Try to enter if no open trade ──────────────────────────
            if not trade_open:
                decision = try_enter_trade(
                    bar_idx   = t,
                    df        = df,
                    surface   = surf,
                    sigma_now = sigma_now,
                    mu_now    = mu_now,
                    p_base    = self.p_base,
                )

                if decision["enter"]:
                    trade_open      = True
                    trade_direction = decision["direction"]
                    entry_price     = df[entry_price_col].iloc[t]
                    trade_start     = t
                else:
                    # Flat bar — record with x=0, p_tp from entry point
                    self.path.append(dict(
                        bar            = t,
                        time           = df.index[t],
                        price          = df[entry_price_col].iloc[t],
                        entry_price    = df[entry_price_col].iloc[t],
                        x              = 0.0,
                        x_clipped      = 0.0,
                        sigma          = sigma_now,
                        sigma_bar      = sbar_now,
                        p_tp           = decision["p_tp_entry"],
                        mu             = mu_now,
                        surface_id     = self.current_surface_id,
                        trade_id       = trade_id,
                        outcome        = None,
                        cumulative_pnl = cumulative_pnl,
                        trade_open     = False,
                        direction      = None,
                    ))
                    continue

            # ── x = displacement from current trade entry ──────────────
            # For shorts, TP is hit when price goes DOWN so flip x
            x_now  = df["close"].iloc[t] - entry_price
            x_high = df["high"].iloc[t]  - entry_price
            x_low  = df["low"].iloc[t]   - entry_price

            if trade_direction == "short":
                x_now  = -x_now
                x_high_orig = x_high
                x_high = -x_low
                x_low  = -x_high_orig

            # ── Query surface ──────────────────────────────────────────
            xg    = surf["x_grid"]
            sg    = surf["s_grid"]
            u     = surf["u"]

            x_c   = np.clip(x_now, xg[0]*0.99, xg[-1]*0.99)
            s_c   = np.clip(sigma_now, sg[0], sg[-1])
            i_now = np.argmin(np.abs(xg - x_c))
            j_now = np.argmin(np.abs(sg - s_c))
            p_tp  = float(u[i_now, j_now])

            # ── Determine exit outcome — check high/low ────────────────
            outcome  = None
            pnl_this = None

            if x_high >= self.p_base.TP and x_low <= self.p_base.SL:
                x_open = df["open"].iloc[t] - entry_price
                if trade_direction == "short":
                    x_open = -x_open
                if abs(x_open - self.p_base.SL) < abs(x_open - self.p_base.TP):
                    outcome  = "SL"
                    pnl_this = self.p_base.SL
                else:
                    outcome  = "TP"
                    pnl_this = self.p_base.TP

            elif x_high >= self.p_base.TP:
                outcome  = "TP"
                pnl_this = self.p_base.TP

            elif x_low <= self.p_base.SL:
                outcome  = "SL"
                pnl_this = self.p_base.SL
            # ── x for recording — use actual exit level if exiting this bar ──
            if outcome == "TP":
                x_record  = self.p_base.TP
                x_clipped_record = self.p_base.TP
            elif outcome == "SL":
                x_record  = self.p_base.SL
                x_clipped_record = self.p_base.SL
            else:
                x_record  = x_now
                x_clipped_record = x_c
            # ── Record bar ────────────────────────────────────────────
            self.path.append(dict(
                bar            = t,
                time           = df.index[t],
                price          = df[entry_price_col].iloc[t],
                entry_price    = entry_price,
                x              = x_record,
                x_clipped      = x_clipped_record,
                sigma          = sigma_now,
                sigma_bar      = sbar_now,
                p_tp           = p_tp,
                mu             = mu_now,
                surface_id     = self.current_surface_id,
                trade_id       = trade_id,
                outcome        = outcome,
                cumulative_pnl = cumulative_pnl,
                trade_open     = True,
                direction      = trade_direction,
            ))

            # ── On exit: record trade and reset ───────────────────────
            if outcome is not None:
                cumulative_pnl += pnl_this
                self.trades.append(dict(
                    trade_id    = trade_id,
                    start_bar   = trade_start,
                    end_bar     = t,
                    n_bars      = t - trade_start,
                    entry_price = entry_price,
                    exit_price  = df[entry_price_col].iloc[t],
                    pnl         = pnl_this,
                    outcome     = outcome,
                    direction   = trade_direction,
                    entry_p_tp  = self.path[
                        next(i for i,p in enumerate(self.path)
                             if p["trade_id"]==trade_id
                             and p["trade_open"])]["p_tp"],
                ))

                trade_open   = False
                entry_price  = None
                trade_id    += 1
                print(f"  Bar {t:>5}  |  {outcome} ({trade_direction})  "
                      f"pnl={pnl_this:+.2f}  "
                      f"cum={cumulative_pnl:+.2f}  "
                      f"trade #{trade_id}")

        self.path_df   = pd.DataFrame(self.path)
        self.trades_df = pd.DataFrame(self.trades) \
                         if self.trades else pd.DataFrame()

        n_tp  = sum(1 for tr in self.trades if tr["outcome"]=="TP")
        n_sl  = sum(1 for tr in self.trades if tr["outcome"]=="SL")
        total = len(self.trades)
        n_flat= len(self.path_df[~self.path_df["trade_open"]]) \
                if "trade_open" in self.path_df.columns else 0

        print(f"\n  Backtest complete")
        print(f"  Surfaces   : {len(self.surfaces)}")
        print(f"  Bars       : {len(self.path_df)}")
        print(f"  Flat bars  : {n_flat}")
        print(f"  Trades     : {total}  "
              f"(TP={n_tp}  SL={n_sl}  "
              f"Win%={n_tp/max(total,1)*100:.1f}%)")
        if total > 0:
            print(f"  Total PnL  : {cumulative_pnl:+.4f}")

        return self.path_df


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main(args={
    "csv"       : "",       # path to CSV or pass DataFrame directly
    "tp"        : 5.5,
    "sl"        : 4.0,
    "mu_col"    : None,     # column name for mu, or None for null
    "threshold" : 1.0,      # vol shift in pts to trigger recompute
    "out"       : "pde_backtest.png",
}):
    import argparse
    a = argparse.Namespace(**args)

    if isinstance(a.csv, pd.DataFrame):
        df = a.csv
    else:
        df = pd.read_csv(a.csv, index_col=0, parse_dates=True)
    df.columns = df.columns.str.lower()

    print(f"  Loaded {len(df)} bars")

    p_base    = Params()
    p_base.TP =  a.tp
    p_base.SL = -a.sl

    if a.mu_col and a.mu_col in df.columns:
        mu_series = df[a.mu_col].fillna(0).values
        print(f"  mu from column: {a.mu_col}")
    else:
        mu_series = np.zeros(len(df))
        print(f"  null model (mu=0)")

    bt      = PDEBacktest(p_base, mu_series,
                          recompute_threshold=a.threshold)
    path_df = bt.run(df, entry_price_col="close")

    surface_stats(bt)
    long_short_analysis(bt)
    plot_backtest(bt, save_path=a.out)
    plot_drawdown(bt, save_path=f"{a.out}_drawdown.png")

    from scipy import stats
    p_null = abs(p_base.SL) / (p_base.TP + abs(p_base.SL))
    edges  = path_df["p_tp"] - p_null
    t_stat, p_val = stats.ttest_1samp(edges, 0)
    print(f"\n  Edge statistics:")
    print(f"  Mean edge  : {edges.mean():+.4f}")
    print(f"  t-stat     : {t_stat:.3f}   p={p_val:.4f}")
    print(f"  Significant: {abs(t_stat) > 1.96}")

    return bt,path_df

if __name__ == "__main__":
    main()