import numpy as np
from strategies.data_structures import EntryFeatures

def create_features(surface, sigma_now, p_base, mu_series, bar_idx):
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

    # ── Pe Calculation ───────────────────────────────────────────────
    L = p_base.TP + abs(p_base.SL)
    pe = abs(mu_series[bar_idx]) * L / (0.5 * sigma_now**2 + 1e-9)

    features = EntryFeatures(
        mu_now     = float(mu_series[bar_idx]),
        sigma_now  = sigma_now,
        sigma_bar  = p.sigma_bar,
        vol_ratio  = vol_ratio,
        pe         = pe,
        p_tp_entry = p_tp_entry,
        p_sl_entry = 1 - p_tp_entry,
        edge_long  = edge_long,
        edge_short = edge_short,
        surface_mu = surface["mu"],
        p_null     = p_null,
    )
    return features