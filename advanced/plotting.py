import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter
import numpy as np
import pandas as pd
from scipy import stats

BG     = "#03060f"
SURF   = "#0a101e"
SURF2  = "#0d1526"
BORDER = "#1a2f50"
ACCENT = "#00d4ff"
ACC2   = "#ff6b35"
ACC3   = "#7fff6b"
ACC4   = "#bf5fff"
WARN   = "#ffcc00"
DANGER = "#ff3860"
LGREY  = "#3a5070"
TWHITE = "#d0e4f7"
TMID   = "#7a9cbd"

CMAP_PROB = LinearSegmentedColormap.from_list(
    "prob", [DANGER, BG, BG, ACC3])

plt.rcParams.update({
    "figure.facecolor": BG,    "axes.facecolor": SURF,
    "text.color": TWHITE,      "font.family": "monospace",
    "axes.labelcolor": TMID,   "xtick.color": TMID,
    "ytick.color": TMID,       "axes.edgecolor": BORDER,
    "grid.color": BORDER,      "grid.linewidth": 0.4,
    "grid.alpha": 0.5,
})

def _sax(ax, title="", xl="", yl=""):
    ax.set_facecolor(SURF)
    for sp in ax.spines.values(): sp.set_edgecolor(BORDER)
    ax.tick_params(colors=TMID, labelsize=7)
    if title: ax.set_title(title, color=TWHITE, fontsize=8,
                           fontweight="bold", pad=4)
    if xl: ax.set_xlabel(xl, color=TMID, fontsize=7)
    if yl: ax.set_ylabel(yl, color=TMID, fontsize=7)
    ax.grid(True)

def plot_backtest(bt, save_path="pde_backtest.png"):

    path_df   = bt.path_df
    trades_df = bt.trades_df
    n_surfaces= len(bt.surfaces)

    if len(path_df) == 0:
        print("  No path data to plot.")
        return

    # ── Figure layout ─────────────────────────────────────────────────
    # Row 0: surface heatmaps (one per computed surface)
    # Row 1: price + trade markers
    # Row 2: P(TP) over time
    # Row 3: x (clipped to [SL,TP]) + cumulative PnL
    # Row 4: vol regime

    n_surf_cols = min(n_surfaces, 4)
    n_surf_rows = max(1, int(np.ceil(n_surfaces / n_surf_cols)))

    surf_h = n_surf_rows * 5.5
    ts_h   = 18
    fig_h  = surf_h + ts_h

    fig = plt.figure(figsize=(max(26, n_surf_cols*7), fig_h))
    fig.patch.set_facecolor(BG)

    fig.text(0.5, 0.998,
             "PDE BACKTEST  ·  u(x,σ)  ·  Trade-Segmented Path Tracking",
             ha="center", va="top", color=ACCENT, fontsize=13,
             fontweight="bold", fontfamily="monospace")

    outer = gridspec.GridSpec(
        2, 1, figure=fig,
        top=0.995, bottom=0.01,
        hspace=0.30,
        height_ratios=[surf_h, ts_h])

    # ══════════════════════════════════════════════════════════════════
    # TOP — surface heatmaps
    # ══════════════════════════════════════════════════════════════════
    surf_grid = gridspec.GridSpecFromSubplotSpec(
        n_surf_rows, n_surf_cols,
        subplot_spec=outer[0],
        wspace=0.28, hspace=0.40)

    path_colors = [ACCENT, ACC2, ACC3, ACC4, WARN,
                   "#ff77ff", "#77ffff", "#ffaa44"]

    for s_idx, surf in enumerate(bt.surfaces):
        row_s = s_idx // n_surf_cols
        col_s = s_idx  % n_surf_cols
        ax    = fig.add_subplot(surf_grid[row_s, col_s])

        u_sm   = gaussian_filter(surf["u"], sigma=0.8)
        xg     = surf["x_grid"]
        sg     = surf["s_grid"]
        p      = surf["p"]

        # Heatmap
        im = ax.imshow(u_sm.T, origin="lower", aspect="auto",
                       extent=[xg[0], xg[-1], sg[0], sg[-1]],
                       cmap=CMAP_PROB, vmin=0, vmax=1)
        cb = fig.colorbar(im, ax=ax, fraction=0.04)
        cb.ax.tick_params(colors=TMID, labelsize=5)
        cb.set_label("P(TP)", color=TMID, fontsize=6)

        # Contours
        XX, SS = np.meshgrid(xg, sg, indexing="ij")
        ct = ax.contour(XX, SS, surf["u"],
                        levels=[0.2,0.3,0.4,0.5,0.6,0.7,0.8],
                        colors=TWHITE, linewidths=0.5, alpha=0.55)
        ax.clabel(ct, fmt="%.1f", colors=TWHITE, fontsize=5)

        # Entry vertical line
        ax.axvline(0, color=WARN, lw=1.0, ls="--", alpha=0.7,
                   label="entry")

        # TP/SL lines
        ax.axvline(p.TP, color=ACC3,   lw=0.9, ls=":", alpha=0.8)
        ax.axvline(p.SL, color=DANGER, lw=0.9, ls=":", alpha=0.8)

        # -- Draw each TRADE's path on this surface separately ----------
        surf_path = path_df[path_df["surface_id"] == s_idx]
        if len(surf_path) > 0:
            for tid, tpath in surf_path.groupby("trade_id"):
                col = path_colors[int(tid) % len(path_colors)]
                xs  = tpath["x_clipped"].values
                ss_ = tpath["sigma"].clip(sg[0], sg[-1]).values

                # Path line
                ax.plot(xs, ss_, color=col,
                        lw=0.9, alpha=0.55, zorder=4)

                # Dots coloured by P(TP)
                ax.scatter(xs, ss_,
                           c=tpath["p_tp"].values,
                           cmap=CMAP_PROB, vmin=0, vmax=1,
                           s=6, alpha=0.75, zorder=5,
                           linewidths=0)

                # Entry dot
                ax.scatter(xs[0], ss_[0],
                           color=col, s=35, marker="^",
                           zorder=8, edgecolors=TWHITE, linewidths=0.4)

                # Exit dot — colour by outcome
                outcome = tpath["outcome"].dropna()
                if len(outcome) > 0:
                    oc  = outcome.iloc[-1]
                    ecol= ACC3 if oc == "TP" else DANGER
                    ax.scatter(xs[-1], ss_[-1],
                               color=ecol, s=40, marker="v",
                               zorder=8, edgecolors=TWHITE,
                               linewidths=0.4)

        # Bar range for this surface
        bar_s = surf["bar"]
        bar_e = (bt.surfaces[s_idx+1]["bar"] - 1
                 if s_idx+1 < len(bt.surfaces)
                 else path_df["bar"].iloc[-1])
        n_trades_on_surf = path_df[
            path_df["surface_id"]==s_idx]["trade_id"].nunique()

        _sax(ax,
             f"Surface {s_idx+1}  bars {bar_s}–{bar_e}\n"
             f"σ̄={p.sigma_bar:.2f}  σ₀={p.sigma0:.2f}  "
             f"μ={surf['mu']:.3f}  trades={n_trades_on_surf}",
             "x  (PnL displacement, resets each trade)", "σ")

        ax.set_xlim(xg[0] - 0.3, xg[-1] + 0.3)
        ax.set_ylim(sg[0], sg[-1])

    # ══════════════════════════════════════════════════════════════════
    # BOTTOM — time series panels
    # ══════════════════════════════════════════════════════════════════
    ts_grid = gridspec.GridSpecFromSubplotSpec(
        5, 1, subplot_spec=outer[1], hspace=0.42)

    bars = path_df["bar"].values

    # ── Panel 1: Price + trade entry/exit markers ──────────────────
    ax1 = fig.add_subplot(ts_grid[0])
    ax1.plot(bars, path_df["price"].values,
             color=ACCENT, lw=0.8, alpha=0.9, zorder=2)

    # Surface recompute lines
    for rb in bt.regimes:
        ax1.axvline(rb, color=WARN, lw=0.7, ls="--",
                    alpha=0.5, zorder=1)

    # Trade entry / exit markers
    if len(trades_df) > 0:
        for _, tr in trades_df.iterrows():
            ecol = ACC3 if tr["outcome"] == "TP" else DANGER
            # entry
            ax1.axvline(tr["start_bar"], color=ACCENT,
                        lw=0.6, ls=":", alpha=0.5)
            # exit marker on price
            exit_price = path_df[
                path_df["bar"] == tr["end_bar"]]["price"]
            if len(exit_price):
                ax1.scatter(tr["end_bar"], exit_price.iloc[0],
                            color=ecol, s=25, zorder=6,
                            marker="x", linewidths=1.2)

    _sax(ax1, "Price  │  yellow=recompute  ✕green=TP  ✕red=SL",
         "", "price")

    # ── Panel 2: x clipped — always in [SL, TP] ───────────────────
    ax2 = fig.add_subplot(ts_grid[1])

    # Colour each trade segment differently
    for tid, tpath in path_df.groupby("trade_id"):
        col = path_colors[int(tid) % len(path_colors)]
        ax2.plot(tpath["bar"].values,
                 tpath["x_clipped"].values,
                 color=col, lw=0.9, alpha=0.8)

        # Mark outcomes
        exits = tpath[tpath["outcome"].notna()]
        for _, row in exits.iterrows():
            ecol = ACC3 if row["outcome"] == "TP" else DANGER
            ax2.scatter(row["bar"], row["x_clipped"],
                        color=ecol, s=40, zorder=7,
                        marker=("^" if row["outcome"]=="TP" else "v"))

    ax2.axhline(bt.p_base.TP, color=ACC3,  lw=1.0,
                ls="--", alpha=0.8, label=f"TP={bt.p_base.TP}")
    ax2.axhline(bt.p_base.SL, color=DANGER,lw=1.0,
                ls="--", alpha=0.8, label=f"SL={bt.p_base.SL}")
    ax2.axhline(0, color=LGREY, lw=0.7, ls=":", alpha=0.6)
    ax2.set_ylim(bt.p_base.SL * 1.15, bt.p_base.TP * 1.15)
    ax2.legend(fontsize=7, facecolor=SURF2, edgecolor=BORDER,
               labelcolor=TWHITE, loc="upper left")
    for rb in bt.regimes:
        ax2.axvline(rb, color=WARN, lw=0.5, ls="--", alpha=0.3)
    _sax(ax2, "x  (PnL displacement — resets on TP/SL hit)",
         "", "x (pts)")

    # ── Panel 3: P(TP) over time ───────────────────────────────────
    ax3 = fig.add_subplot(ts_grid[2])
    p_null = abs(bt.p_base.SL) / (bt.p_base.TP + abs(bt.p_base.SL))

    for tid, tpath in path_df.groupby("trade_id"):
        col = path_colors[int(tid) % len(path_colors)]
        ax3.plot(tpath["bar"].values, tpath["p_tp"].values,
                 color=col, lw=0.9, alpha=0.8)

    ax3.axhline(0.5,   color=ACC3,  lw=0.9, ls="--",
                alpha=0.8, label="P=0.5")
    ax3.axhline(p_null,color=LGREY, lw=0.8, ls=":",
                alpha=0.7, label=f"null={p_null:.3f}")
    ax3.set_ylim(0, 1)
    ax3.legend(fontsize=7, facecolor=SURF2, edgecolor=BORDER,
               labelcolor=TWHITE, loc="upper left")
    for rb in bt.regimes:
        ax3.axvline(rb, color=WARN, lw=0.5, ls="--", alpha=0.3)
    _sax(ax3, "P(TP | x, σ)  per trade (colour = trade ID)",
         "", "P(TP)")

    # ── Panel 4: Cumulative PnL ────────────────────────────────────
    ax4 = fig.add_subplot(ts_grid[3])
    cum = path_df["cumulative_pnl"].values
    col_line = np.where(cum >= 0, ACC3, DANGER)
    ax4.plot(bars, cum, color=ACC3, lw=1.0, alpha=0.9)
    ax4.fill_between(bars, cum, 0,
                     where=cum >= 0, alpha=0.15, color=ACC3)
    ax4.fill_between(bars, cum, 0,
                     where=cum <  0, alpha=0.15, color=DANGER)
    ax4.axhline(0, color=LGREY, lw=0.8, ls=":", alpha=0.7)
    for rb in bt.regimes:
        ax4.axvline(rb, color=WARN, lw=0.5, ls="--", alpha=0.3)
    if len(trades_df) > 0:
        for _, tr in trades_df.iterrows():
            ecol = ACC3 if tr["outcome"]=="TP" else DANGER
            cum_at_exit = path_df[
                path_df["bar"]==tr["end_bar"]]["cumulative_pnl"]
            if len(cum_at_exit):
                ax4.scatter(tr["end_bar"], cum_at_exit.iloc[0],
                            color=ecol, s=30, zorder=6, marker="o")
    _sax(ax4, "Cumulative PnL  (green dot=TP  red dot=SL)",
         "", "PnL (pts)")

    # ── Panel 5: Vol regime ────────────────────────────────────────
    ax5 = fig.add_subplot(ts_grid[4])
    ax5.plot(bars, path_df["sigma"].values,
             color=ACCENT, lw=0.7, alpha=0.8, label="σ current")
    ax5.plot(bars, path_df["sigma_bar"].values,
             color=WARN,   lw=1.0, alpha=0.9, label="σ̄ long-run")
    for rb in bt.regimes:
        ax5.axvline(rb, color=WARN, lw=0.8,
                    ls="--", alpha=0.6)
    ax5.legend(fontsize=7, facecolor=SURF2, edgecolor=BORDER,
               labelcolor=TWHITE)
    _sax(ax5, "Volatility Regime  (yellow = recompute trigger)",
         "bar", "σ (pts)")

    # ── Summary box ────────────────────────────────────────────────
    if len(trades_df) > 0:
        n_tp   = (trades_df["outcome"]=="TP").sum()
        n_sl   = (trades_df["outcome"]=="SL").sum()
        total  = len(trades_df)
        tot_pnl= trades_df["pnl"].sum()
        avg_dur= trades_df["n_bars"].mean()
        ptp_s  = path_df["p_tp"]
        p_null = abs(bt.p_base.SL)/(bt.p_base.TP+abs(bt.p_base.SL))
        m_edge = (ptp_s - p_null).mean()
    else:
        n_tp=n_sl=total=0; tot_pnl=0; avg_dur=0; m_edge=0

    summary = (
        f"  BACKTEST SUMMARY\n"
        f"  ─────────────────────────────\n"
        f"  Trades     : {total}\n"
        f"  TP hits    : {n_tp}  ({n_tp/max(total,1)*100:.1f}%)\n"
        f"  SL hits    : {n_sl}  ({n_sl/max(total,1)*100:.1f}%)\n"
        f"  Total PnL  : {tot_pnl:+.2f} pts\n"
        f"  Avg duration: {avg_dur:.1f} bars\n"
        f"  Mean edge  : {m_edge:+.4f}\n"
        f"  ─────────────────────────────\n"
        f"  TP={bt.p_base.TP}  SL={bt.p_base.SL}\n"
        f"  Surfaces   : {len(bt.surfaces)}\n"
        f"  Threshold  : {bt.threshold} pts"
    )
    fig.text(0.78, 0.015, summary,
             color=TWHITE, fontsize=8,
             fontfamily="monospace", va="bottom",
             bbox=dict(boxstyle="round,pad=0.6",
                       facecolor=SURF2,
                       edgecolor=ACCENT, alpha=0.9))

    plt.savefig(save_path, dpi=110, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"\n  ✔  Saved → {save_path}")

def surface_stats(bt):
    path_df   = bt.path_df
    trades_df = bt.trades_df
    p_null    = abs(bt.p_base.SL) / (bt.p_base.TP + abs(bt.p_base.SL))

    print(f"\n{'═'*65}")
    print(f"  SURFACE-WISE STATISTICS")
    print(f"{'═'*65}")
    print(f"  {'Surf':>4}  {'Bars':>5}  {'Trades':>6}  "
          f"{'TP%':>5}  {'PnL':>7}  {'MeanP':>7}  "
          f"{'Edge':>7}  {'t':>6}  {'p':>6}")
    print(f"  {'─'*60}")

    for s_idx, surf in enumerate(bt.surfaces):
        sp     = path_df[path_df["surface_id"] == s_idx]
        st     = trades_df[trades_df["trade_id"].isin(
                     sp["trade_id"].unique())] \
                 if len(trades_df) > 0 else pd.DataFrame()

        n_bars = len(sp)
        n_tr   = len(st)
        n_tp   = (st["outcome"]=="TP").sum() if n_tr>0 else 0
        pnl    = st["pnl"].sum()             if n_tr>0 else 0
        tp_pct = n_tp / max(n_tr,1) * 100

        edges  = sp["p_tp"] - p_null
        m_edge = edges.mean()
        m_ptp  = sp["p_tp"].mean()

        if len(edges) > 1:
            t_s, p_s = stats.ttest_1samp(edges, 0)
        else:
            t_s, p_s = 0.0, 1.0

        sig = "***" if p_s<0.001 else "**" if p_s<0.01 \
              else "*" if p_s<0.05 else ""

        print(f"  {s_idx+1:>4}  {n_bars:>5}  {n_tr:>6}  "
              f"{tp_pct:>5.1f}  {pnl:>+7.2f}  {m_ptp:>7.4f}  "
              f"{m_edge:>+7.4f}  {t_s:>6.2f}  {p_s:>6.4f}  {sig}")

        p = surf["p"]
        print(f"        σ̄={p.sigma_bar:.3f}  "
              f"σ₀={p.sigma0:.3f}  "
              f"η={p.eta:.3f}  "
              f"β={p.beta:.4f}  "
              f"ρ={p.rho:.3f}  "
              f"μ={surf['mu']:.4f}")

    print(f"{'═'*65}")

def long_short_analysis(bt):
    """
    Breaks down performance by trade direction (long vs short).
    Only meaningful if your try_enter_trade returns both directions.
    """
    from scipy import stats

    trades_df = bt.trades_df
    path_df   = bt.path_df
    p_null    = abs(bt.p_base.SL) / (bt.p_base.TP + abs(bt.p_base.SL))

    if len(trades_df) == 0:
        print("  No trades to analyse.")
        return

    # If direction column missing, everything is long
    if "direction" not in trades_df.columns:
        trades_df["direction"] = "long"
    if "direction" not in path_df.columns:
        path_df["direction"] = "long"

    directions = trades_df["direction"].unique()

    print(f"\n{'═'*65}")
    print(f"  LONG vs SHORT ANALYSIS")
    print(f"{'═'*65}")
    print(f"  Break-even win rate : {p_null:.4f} "
          f"({p_null*100:.1f}%)")
    print(f"  TP={bt.p_base.TP}  SL={bt.p_base.SL}  "
          f"R:R = {bt.p_base.TP/abs(bt.p_base.SL):.2f}")
    print()

    for direction in ["long", "short"]:
        t_dir = trades_df[trades_df["direction"] == direction]
        p_dir = path_df[path_df["direction"] == direction]

        if len(t_dir) == 0:
            print(f"  {direction.upper():5}  — no trades")
            continue

        n_total = len(t_dir)
        n_tp    = (t_dir["outcome"] == "TP").sum()
        n_sl    = (t_dir["outcome"] == "SL").sum()
        win_pct = n_tp / n_total
        total_pnl = t_dir["pnl"].sum()
        avg_pnl   = t_dir["pnl"].mean()
        avg_dur   = t_dir["n_bars"].mean()

        # t-test: is win rate significantly above break-even
        wins   = (t_dir["outcome"] == "TP").astype(int).values
        t_stat, p_val = stats.ttest_1samp(wins, popmean=p_null)

        # Edge from PDE surface
        edges = p_dir["p_tp"] - p_null
        mean_edge = edges.mean()
        t_edge, p_edge = stats.ttest_1samp(edges, 0)

        # Consecutive win/loss streaks
        outcomes = (t_dir["outcome"] == "TP").astype(int).values
        max_wins  = max((sum(1 for _ in g)
                         for k,g in __import__('itertools').groupby(outcomes)
                         if k == 1), default=0)
        max_losses= max((sum(1 for _ in g)
                         for k,g in __import__('itertools').groupby(outcomes)
                         if k == 0), default=0)

        # Sharpe-like per trade
        pnl_std = t_dir["pnl"].std()
        sharpe  = avg_pnl / (pnl_std + 1e-9) * np.sqrt(n_total)

        marker = "✔" if win_pct > p_null else "✗"
        sig    = ("***" if p_val < 0.001 else
                  "**"  if p_val < 0.01  else
                  "*"   if p_val < 0.05  else "")

        print(f"  {'─'*60}")
        print(f"  {direction.upper()}  {marker}  "
              f"Win%={win_pct*100:.1f}%  "
              f"(break-even={p_null*100:.1f}%)  {sig}")
        print(f"  {'─'*60}")
        print(f"  Trades      : {n_total}  "
              f"(TP={n_tp}  SL={n_sl})")
        print(f"  Total PnL   : {total_pnl:+.2f} pts")
        print(f"  Avg PnL     : {avg_pnl:+.4f} pts/trade")
        print(f"  Avg duration: {avg_dur:.1f} bars")
        print(f"  Sharpe      : {sharpe:+.3f}")
        print(f"  Win rate t  : t={t_stat:.3f}  p={p_val:.4f}")
        print(f"  Mean PDE edge : {mean_edge:+.4f}  "
              f"t={t_edge:.3f}  p={p_edge:.4f}")
        print(f"  Max win streak  : {max_wins}")
        print(f"  Max loss streak : {max_losses}")

        # Breakdown by vol regime
        print(f"\n  By vol ratio (σ₀/σ̄):")
        print(f"  {'Range':<15} {'Trades':>6} {'Win%':>6} "
              f"{'PnL':>8} {'AvgPnL':>8}")
        print(f"  {'─'*45}")

        vol_bins  = [0, 0.5, 1.0, 1.5, 2.0, 999]
        vol_labels= ["<0.5","0.5-1","1-1.5","1.5-2",">2"]

        if "sigma" in p_dir.columns and "sigma_bar" in p_dir.columns:
            # Map vol ratio at trade start to each trade
            trade_vr = {}
            for tid in t_dir["trade_id"]:
                tb = p_dir[p_dir["trade_id"] == tid]
                if len(tb):
                    vr = (tb["sigma"].iloc[0] /
                          (tb["sigma_bar"].iloc[0] + 1e-9))
                    trade_vr[tid] = vr
            t_dir_vr = t_dir.copy()
            t_dir_vr["vol_ratio"] = t_dir_vr["trade_id"].map(trade_vr)

            for lo, hi, lbl in zip(vol_bins[:-1], vol_bins[1:], vol_labels):
                mask = ((t_dir_vr["vol_ratio"] >= lo) &
                        (t_dir_vr["vol_ratio"] <  hi))
                sub  = t_dir_vr[mask]
                if len(sub) == 0:
                    continue
                w    = (sub["outcome"]=="TP").mean()
                pnl_ = sub["pnl"].sum()
                apnl = sub["pnl"].mean()
                mk   = "✔" if w > p_null else "✗"
                print(f"  {lbl:<15} {len(sub):>6} "
                      f"{w*100:>5.1f}% "
                      f"{pnl_:>+8.1f} "
                      f"{apnl:>+8.3f}  {mk}")

    # ── Side by side summary ──────────────────────────────────────
    print(f"\n  {'─'*65}")
    print(f"  SUMMARY")
    print(f"  {'─'*65}")
    print(f"  {'':20} {'LONG':>12} {'SHORT':>12} {'COMBINED':>12}")
    print(f"  {'─'*60}")

    for col, label, fmt in [
        ("outcome", "Trades",   None),
        ("outcome", "Win%",     None),
        ("pnl",     "Total PnL","+.1f"),
        ("pnl",     "Avg PnL",  "+.3f"),
        ("n_bars",  "Avg bars",  ".1f"),
    ]:
        longs  = trades_df[trades_df["direction"]=="long"]
        shorts = trades_df[trades_df["direction"]=="short"]

        if label == "Trades":
            lv = str(len(longs))
            sv = str(len(shorts))
            cv = str(len(trades_df))
        elif label == "Win%":
            lw = (longs["outcome"]=="TP").mean()*100 if len(longs) else 0
            sw = (shorts["outcome"]=="TP").mean()*100 if len(shorts) else 0
            cw = (trades_df["outcome"]=="TP").mean()*100
            lv = f"{lw:.1f}%"
            sv = f"{sw:.1f}%"
            cv = f"{cw:.1f}%"
        elif label == "Total PnL":
            lv = f"{longs['pnl'].sum():+.1f}" if len(longs) else "n/a"
            sv = f"{shorts['pnl'].sum():+.1f}" if len(shorts) else "n/a"
            cv = f"{trades_df['pnl'].sum():+.1f}"
        elif label == "Avg PnL":
            lv = f"{longs['pnl'].mean():+.3f}" if len(longs) else "n/a"
            sv = f"{shorts['pnl'].mean():+.3f}" if len(shorts) else "n/a"
            cv = f"{trades_df['pnl'].mean():+.3f}"
        elif label == "Avg bars":
            lv = f"{longs['n_bars'].mean():.1f}" if len(longs) else "n/a"
            sv = f"{shorts['n_bars'].mean():.1f}" if len(shorts) else "n/a"
            cv = f"{trades_df['n_bars'].mean():.1f}"

        print(f"  {label:<20} {lv:>12} {sv:>12} {cv:>12}")

    print(f"{'═'*65}")

def plot_drawdown(bt, save_path="drawdown.png"):
    path_df = bt.path_df

    # Compute running max and drawdown from cumulative PnL
    cum     = path_df["cumulative_pnl"].values
    bars    = path_df["bar"].values
    run_max = np.maximum.accumulate(cum)
    dd      = cum - run_max          # always <= 0
    max_dd  = dd.min()
    max_dd_bar = bars[np.argmin(dd)]

    # Peak before max drawdown
    peak_bar = bars[np.argmax(cum[:np.argmin(dd)+1])]

    fig, axes = plt.subplots(2, 1, figsize=(18, 10),
                              facecolor=BG)
    fig.suptitle("DRAWDOWN ANALYSIS", color=ACCENT,
                 fontsize=12, fontweight="bold",
                 fontfamily="monospace")

    # ── Panel 1: Cumulative PnL with drawdown shading ─────────────
    ax1 = axes[0]
    ax1.set_facecolor(SURF)
    ax1.plot(bars, cum,     color=ACC3,  lw=1.0, label="Cum PnL")
    ax1.plot(bars, run_max, color=ACCENT,lw=0.8,
             ls="--", alpha=0.7, label="Running max")
    ax1.fill_between(bars, cum, run_max,
                     alpha=0.25, color=DANGER, label="Drawdown")
    ax1.axvline(max_dd_bar, color=DANGER, lw=1.2,
                ls="--", alpha=0.9,
                label=f"Max DD bar={max_dd_bar}")
    ax1.axvline(peak_bar,   color=WARN,  lw=1.0,
                ls=":",  alpha=0.8,
                label=f"Peak bar={peak_bar}")
    ax1.axhline(0, color=LGREY, lw=0.7, ls=":", alpha=0.6)
    ax1.legend(fontsize=7, facecolor=SURF2,
               edgecolor=BORDER, labelcolor=TWHITE)
    for sp in ax1.spines.values(): sp.set_edgecolor(BORDER)
    ax1.tick_params(colors=TMID, labelsize=7)
    ax1.set_ylabel("PnL (pts)", color=TMID, fontsize=7)
    ax1.set_title("Cumulative PnL  +  Drawdown Region",
                  color=TWHITE, fontsize=8, fontweight="bold")
    ax1.grid(True, color=BORDER, alpha=0.5)

    # Surface recompute markers
    for rb in bt.regimes:
        ax1.axvline(rb, color=WARN, lw=0.5,
                    ls="--", alpha=0.3)

    # ── Panel 2: Drawdown series ───────────────────────────────────
    ax2 = axes[1]
    ax2.set_facecolor(SURF)
    ax2.plot(bars, dd, color=DANGER, lw=0.9, alpha=0.9)
    ax2.fill_between(bars, dd, 0,
                     alpha=0.3, color=DANGER)
    ax2.axhline(max_dd, color=WARN, lw=1.0, ls="--",
                label=f"Max DD = {max_dd:.2f} pts")
    ax2.axhline(max_dd * 0.5, color=LGREY, lw=0.7,
                ls=":", alpha=0.7,
                label=f"50% of max DD = {max_dd*0.5:.2f}")
    ax2.axvline(max_dd_bar, color=DANGER, lw=1.2,
                ls="--", alpha=0.9)
    ax2.legend(fontsize=7, facecolor=SURF2,
               edgecolor=BORDER, labelcolor=TWHITE)
    for sp in ax2.spines.values(): sp.set_edgecolor(BORDER)
    ax2.tick_params(colors=TMID, labelsize=7)
    ax2.set_xlabel("bar", color=TMID, fontsize=7)
    ax2.set_ylabel("Drawdown (pts)", color=TMID, fontsize=7)
    ax2.set_title("Drawdown from Peak",
                  color=TWHITE, fontsize=8, fontweight="bold")
    ax2.grid(True, color=BORDER, alpha=0.5)

    for rb in bt.regimes:
        ax2.axvline(rb, color=WARN, lw=0.5,
                    ls="--", alpha=0.3)

    # ── Stats box ─────────────────────────────────────────────────
    # Calmar = annualised return / max drawdown
    total_pnl = cum[-1]
    calmar    = total_pnl / abs(max_dd) if max_dd != 0 else 0

    # Average drawdown
    avg_dd    = dd[dd < 0].mean() if (dd < 0).any() else 0

    # Time underwater — bars where cum < running max
    pct_under = (dd < 0).mean() * 100

    # Recovery — bars from max DD to new equity high
    post_dd   = cum[np.argmin(dd):]
    rec_bars  = next((i for i,v in enumerate(post_dd)
                      if v >= run_max[np.argmin(dd)]), None)

    box = (
        f"  Max drawdown  : {max_dd:.2f} pts\n"
        f"  Avg drawdown  : {avg_dd:.2f} pts\n"
        f"  Total PnL     : {total_pnl:+.2f} pts\n"
        f"  Calmar ratio  : {calmar:.3f}\n"
        f"  Time underwater: {pct_under:.1f}%\n"
        f"  Recovery bars : "
        f"{'not yet' if rec_bars is None else rec_bars}"
    )
    fig.text(0.76, 0.12, box, color=TWHITE, fontsize=8,
             fontfamily="monospace", va="bottom",
             bbox=dict(boxstyle="round,pad=0.6",
                       facecolor=SURF2,
                       edgecolor=ACCENT, alpha=0.9))

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(save_path, dpi=110, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"  ✔  Drawdown chart → {save_path}")