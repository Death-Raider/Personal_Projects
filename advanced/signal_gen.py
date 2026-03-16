import numpy as np

def try_enter_trade(bar_idx, df, surface, sigma_now, mu_now, p_base):
    """
    Decides whether to enter a trade at the current bar.
    Called by the backtest engine every time there is no open position.

    Returns a dict:
        enter     : bool   — whether to open a trade
        direction : "long" | "short"
        reason    : str    — human-readable explanation

    Parameters
    ----------
    bar_idx   : current bar index into df
    df        : full OHLCV dataframe
    surface   : current PDE surface dict with keys u, x_grid, s_grid, p
    sigma_now : current volatility estimate (price units)
    mu_now    : current drift estimate from model
    p_base    : Params object with TP, SL

    The surface gives you u(x=0, sigma_now) = P(TP | just entered).
    The null P(TP) = |SL| / (TP + |SL|).
    Edge = u(x=0, sigma_now) - null.

    ── HOW TO CUSTOMISE ────────────────────────────────────────────────
    This function is the ONLY place you need to change to test a strategy.
    The backtest engine calls it on every bar when no trade is open.
    Return enter=True to open a trade, False to stay flat.

    Example strategies you can implement here:
        Null (always enter):
            return {"enter": True, "direction": "long", "reason": "null"}

        PDE edge threshold:
            enter if p_tp_entry > null + 0.05

        Vol regime filter:
            enter only if sigma0 / sigma_bar > 1.5 (vol spike mean-reverting)

        Direction from mu:
            long  if mu > 0 and p_tp_entry > null
            short if mu < 0 and p_sl_entry > null

        Combined:
            all of the above simultaneously
    ────────────────────────────────────────────────────────────────────
    """
    u       = surface["u"]
    x_grid  = surface["x_grid"]
    s_grid  = surface["s_grid"]
    p       = surface["p"]

    # ── Query surface at entry point x=0 ──────────────────────────────
    i0       = np.argmin(np.abs(x_grid - 0.0))
    j0       = np.argmin(np.abs(s_grid - np.clip(sigma_now,
                                                   s_grid[0], s_grid[-1])))
    p_tp_entry = float(u[i0, j0])
    p_sl_entry = 1.0 - p_tp_entry

    # ── Null probability ───────────────────────────────────────────────
    p_null     = abs(p_base.SL) / (p_base.TP + abs(p_base.SL))
    edge_long  = p_tp_entry - p_null
    edge_short = p_sl_entry - p_null

    # ── Vol regime ratio ───────────────────────────────────────────────
    vol_ratio  = sigma_now / (p.sigma_bar + 1e-9)

    # Do not enter if current bar range already spans boundaries
    bar_range = df["high"].iloc[bar_idx] - df["low"].iloc[bar_idx]
    if bar_range >= (p_base.TP + abs(p_base.SL)) * 0.8:
        return dict(enter=False, direction=None,
                    reason=f"bar range {bar_range:.2f} too wide",
                    p_tp_entry=p_tp_entry, edge=edge_long,
                    vol_ratio=vol_ratio)
    # ══════════════════════════════════════════════════════════════════
    # ── STRATEGY LOGIC — EDIT THIS SECTION ────────────────────────────
    # ══════════════════════════════════════════════════════════════════

    # --- NULL STRATEGY: always enter long (baseline) ------------------
    # return dict(
    #     enter       = True,
    #     direction   = "long",
    #     reason      = "null — always enter",
    #     p_tp_entry  = p_tp_entry,
    #     edge        = edge_long,
    #     vol_ratio   = vol_ratio,
    # )

    # --- PDE EDGE STRATEGY (uncomment to use) -------------------------
    # EDGE_THRESHOLD = 0.05
    # if edge_long > EDGE_THRESHOLD:
    #     return dict(enter=True, direction="long",
    #                 reason=f"long edge={edge_long:.3f}",
    #                 p_tp_entry=p_tp_entry, edge=edge_long,
    #                 vol_ratio=vol_ratio)
    # elif edge_short > EDGE_THRESHOLD:
    #     return dict(enter=True, direction="short",
    #                 reason=f"short edge={edge_short:.3f}",
    #                 p_tp_entry=p_sl_entry, edge=edge_short,
    #                 vol_ratio=vol_ratio)
    # else:
    #     return dict(enter=False, direction=None,
    #                 reason=f"no edge: long={edge_long:.3f} short={edge_short:.3f}",
    #                 p_tp_entry=p_tp_entry, edge=max(edge_long,edge_short),
    #                 vol_ratio=vol_ratio)

    # --- VOL REGIME STRATEGY (uncomment to use) -----------------------
    # VOL_RATIO_THRESHOLD = 1.5
    # if vol_ratio > VOL_RATIO_THRESHOLD:
    #     return dict(enter=True, direction="long",
    #                 reason=f"vol spike ratio={vol_ratio:.2f}",
    #                 p_tp_entry=p_tp_entry, edge=edge_long,
    #                 vol_ratio=vol_ratio)
    # else:
    #     return dict(enter=False, direction=None,
    #                 reason=f"vol ratio too low: {vol_ratio:.2f}",
    #                 p_tp_entry=p_tp_entry, edge=edge_long,
    #                 vol_ratio=vol_ratio)

    # --- MU DIRECTION STRATEGY (uncomment to use) ---------------------
    MU_THRESHOLD   = 0.05
    EDGE_THRESHOLD = 0.03
    VOL_MAX        = 1.5
    VOL_STRONG     = 1.0
    P_THRESHOLD    = 0.46

    # 1️⃣ Volatility regime filter
    if vol_ratio > VOL_MAX:
        return dict(
            enter=False,
            direction=None,
            reason=f"vol too high: {vol_ratio:.2f}",
            p_tp_entry=p_tp_entry,
            edge=0.0,
            vol_ratio=vol_ratio
        )

    # 2️⃣ Directional bias from drift
    long_bias  = mu_now > MU_THRESHOLD
    short_bias = mu_now < -MU_THRESHOLD

    # 3️⃣ Strong regime (best performance)
    if vol_ratio < VOL_STRONG:

        if long_bias and edge_long > EDGE_THRESHOLD and p_tp_entry > P_THRESHOLD:
            return dict(
                enter=True,
                direction="long",
                reason=f"strong regime long μ={mu_now:.3f}",
                p_tp_entry=p_tp_entry,
                edge=edge_long,
                vol_ratio=vol_ratio
            )

        if short_bias and edge_short > EDGE_THRESHOLD and p_sl_entry > P_THRESHOLD:
            return dict(
                enter=True,
                direction="short",
                reason=f"strong regime short μ={mu_now:.3f}",
                p_tp_entry=p_sl_entry,
                edge=edge_short,
                vol_ratio=vol_ratio
            )

    # 4️⃣ Moderate regime (require stronger edge)
    if edge_long > EDGE_THRESHOLD * 1.5 and p_tp_entry > P_THRESHOLD + 0.02:
        if mu_now > 0:
            return dict(
                enter=True,
                direction="long",
                reason=f"moderate regime long μ={mu_now:.3f}",
                p_tp_entry=p_tp_entry,
                edge=edge_long,
                vol_ratio=vol_ratio
            )

    if edge_short > EDGE_THRESHOLD * 1.5 and p_sl_entry > P_THRESHOLD + 0.02:
        if mu_now < 0:
            return dict(
                enter=True,
                direction="short",
                reason=f"moderate regime short μ={mu_now:.3f}",
                p_tp_entry=p_sl_entry,
                edge=edge_short,
                vol_ratio=vol_ratio
            )

    # 5️⃣ No signal
    return dict(
        enter=False,
        direction=None,
        reason=f"no signal μ={mu_now:.3f}",
        p_tp_entry=p_tp_entry,
        edge=0.0,
        vol_ratio=vol_ratio
    )

    # ══════════════════════════════════════════════════════════════════