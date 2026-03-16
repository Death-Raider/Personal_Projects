import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from scipy.linalg import solve_banded
from scipy.ndimage import gaussian_filter
import warnings
warnings.filterwarnings("ignore")

# ── Palette ────────────────────────────────────────────────────────────────
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
    "prob", ["#ff3860", "#03060f", "#03060f", "#7fff6b"])
CMAP_VOL  = LinearSegmentedColormap.from_list(
    "vol",  ["#0a101e", "#00d4ff", "#ffcc00", "#ff6b35"])

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": SURF,
    "text.color": TWHITE,   "font.family": "monospace",
    "axes.labelcolor": TMID,"xtick.color": TMID,
    "ytick.color": TMID,    "axes.edgecolor": BORDER,
    "grid.color": BORDER,   "grid.linewidth": 0.4,
    "grid.alpha": 0.5,
})

def _sax(ax, title="", xl="", yl="", grid=True):
    ax.set_facecolor(SURF)
    for sp in ax.spines.values(): sp.set_edgecolor(BORDER)
    ax.tick_params(colors=TMID, labelsize=7)
    if title: ax.set_title(title, color=TWHITE, fontsize=8, fontweight="bold", pad=4)
    if xl: ax.set_xlabel(xl, color=TMID, fontsize=7)
    if yl: ax.set_ylabel(yl, color=TMID, fontsize=7)
    if grid: ax.grid(True)

# ══════════════════════════════════════════════════════════════════════════════
# EDGE DEFINING MODELS
# ══════════════════════════════════════════════════════════════════════════════

MU = 0.05

null         = lambda p_self,x, sigma, t: np.zeros_like(x)
fixed_edge   = lambda p_self,x, sigma, t: np.full_like(x, MU)
vol_adjusted = lambda p_self,x, sigma, t: 0.15 / (sigma + 1e-6)
mean_rev     = lambda p_self,x, sigma, t: -0.05 * x

# Full model M — takes features, returns drift
def model_M(params, features_fn):
    def mu_fn(p_self,x, sigma, t):
        features = features_fn(x, sigma, t)
        return (params["w_mom"]   * features["mom"]
              + params["w_trend"] * features["trend"]
              + params["w_vol"]   * (sigma - p.sigma_bar))
    return mu_fn

# ══════════════════════════════════════════════════════════════════════════════
# PARAMETERS
# ══════════════════════════════════════════════════════════════════════════════

class Params:
    # Trade boundaries (in price units / pips / points)
    S    = 5018.70  # initial spot price (for scaling)
    TP   =  5.5       # take-profit
    SL   = -4       # stop-loss  (negative)

    # Stochastic vol (CIR-like mean-reversion on σ)
    mu        = MU
    beta      = 0.02088 # 0.031  # mean-reversion speed
    sigma_bar = 3.9648 # 0.00834 * S   # long-run vol level
    eta       = 0.16703 # 0.00214 * S   # vol-of-vol
    sigma0    = 3.8989 # 0.00323 * S   # initial σ
    mu_fn     = fixed_edge   # drift in price (set to 0 for pure exit problem)
    r_kill = 0.1     # tune this — higher = more time-pressure

    # Correlation between price and vol innovations
    rho     =  0.01283221 # 0.413    # typically negative (leverage effect)

    # Simulation
    T       = 1/r_kill    # time horizon (long enough to capture most exits)
    dt      = 1e-4    # Euler-Maruyama time step
    N_paths = 3000    # Monte Carlo paths
    seed    = 42

    # PDE grid
    Nx      = 100     # grid points in X
    Ns      = 100      # grid points in σ
    sigma_max = 5   # upper bound for σ grid

P = Params()


# ══════════════════════════════════════════════════════════════════════════════
# 1.  EULER-MARUYAMA MONTE CARLO
# ══════════════════════════════════════════════════════════════════════════════

def run_monte_carlo(p: Params = Params(), x0=0.0):
    """
    Simulate N_paths trajectories of (X_t, σ_t) until exit or T.

    Returns
    -------
    paths_x   : (N_paths, steps+1)  — X paths (NaN after exit)
    paths_sig : (N_paths, steps+1)  — σ paths
    exit_val  : (N_paths,)          — +TP, -SL, or NaN (no exit)
    exit_time : (N_paths,)          — exit time or NaN
    """
    rng   = np.random.default_rng(p.seed)
    steps = int(p.T / p.dt)

    sdt   = np.sqrt(p.dt)

    X   = np.full(p.N_paths, x0,      dtype=np.float64)
    sig = np.full(p.N_paths, p.sigma0, dtype=np.float64)

    paths_x   = np.full((p.N_paths, steps + 1), np.nan)
    paths_sig = np.full((p.N_paths, steps + 1), np.nan)
    paths_x[:, 0]   = X
    paths_sig[:, 0] = sig

    exit_val  = np.full(p.N_paths, np.nan)
    exit_time = np.full(p.N_paths, np.nan)
    active    = np.ones(p.N_paths, dtype=bool)

    for i in range(1, steps + 1):
        if not active.any():
            break

        n_act = active.sum()
        # Correlated Brownian increments
        Z1 = rng.standard_normal(n_act)
        Z2 = rng.standard_normal(n_act)
        dW1 = sdt * Z1
        dW2 = sdt * (p.rho * Z1 + np.sqrt(1 - p.rho**2) * Z2)

        sig_a = sig[active]
        X_a   = X[active]

        # dX = mu*dt + σ dW1
        time_new = i * p.dt
        mu_t  = p.mu_fn(X_a, sig_a, time_new)
        X_new = X_a + mu_t * p.dt + sig_a * dW1

        # dσ = β(σ̄ - σ) dt + η dW2  (reflected at 0 to keep σ > 0)
        sig_new = sig_a + p.beta * (p.sigma_bar - sig_a) * p.dt + p.eta * dW2
        sig_new = np.abs(sig_new)   # reflection at 0 (simple positivity enforcement)

        X[active]   = X_new
        sig[active] = sig_new

        paths_x[active, i]   = X_new
        paths_sig[active, i] = sig_new

        # Check boundary hits
        hit_tp = active & (X >= p.TP)
        hit_sl = active & (X <= p.SL)
        hit    = hit_tp | hit_sl

        exit_val[hit_tp]  = p.TP
        exit_val[hit_sl]  = p.SL
        exit_time[hit]    = i * p.dt
        active[hit]       = False

    return paths_x, paths_sig, exit_val, exit_time


# ══════════════════════════════════════════════════════════════════════════════
# 2.  PDE  —  KOLMOGOROV BACKWARD EQUATION
# ══════════════════════════════════════════════════════════════════════════════
#
# Let u(x, σ) = P(exit at TP before SL | X=x, σ=σ)
#
# The infinitesimal generator of (X, σ) applied to u gives:
#
#   0 = ½σ²u_xx + μu_x + β(σ̄-σ)u_σ + ½η²u_σσ + ρσηu_xσ - ru
#
# on domain  x ∈ (SL, TP),  σ ∈ (0, σ_max)
#
# Boundary conditions:
#   u(TP, σ)  = 1   for all σ    (hit TP → success)
#   u(SL, σ)  = 0   for all σ    (hit SL → failure)
#   u_σ(x, 0) = 0               (reflecting at σ=0, Neumann)
#   u_σ(x, σ_max) = 0           (Neumann at upper σ boundary)
#
# Solved by iterative ADI (Alternating Direction Implicit) or
# direct sparse solve on the flattened 2D grid.
# ══════════════════════════════════════════════════════════════════════════════

def solve_pde(p: Params):
    """
    Direct sparse solve of the Kolmogorov backward equation for
    u(x, σ) = P(exit at TP before SL | X=x, σ=σ).

    Generator equation (zero drift in X):
        ½σ² u_xx  +  β(σ̄−σ) u_σ  +  ½η² u_σσ  +  ρση u_xσ  =  0

    Discretised on interior grid and solved as a linear system Au = b.
    """
    from scipy.sparse import lil_matrix
    from scipy.sparse.linalg import spsolve

    x_grid = np.linspace(p.SL, p.TP,       p.Nx)
    s_grid = np.linspace(1e-3, p.sigma_max, p.Ns)
    dx = x_grid[1] - x_grid[0]
    ds = s_grid[1] - s_grid[0]

    # Only interior x-nodes (i=1..Nx-2); all σ-nodes
    Ni = p.Nx - 2   # interior x points
    Nj = p.Ns       # all σ points
    N  = Ni * Nj    # total unknowns

    def idx(i, j):   # i in 0..Ni-1  (maps to x_grid[i+1])
        return i * Nj + j

    A = lil_matrix((N, N))
    b = np.zeros(N)

    for i in range(Ni):
        xi = i + 1              # index into x_grid
        for j in range(Nj):
            sig = s_grid[j]
            row = idx(i, j)
            x   = x_grid[i + 1]
            mu  = p.mu_fn(x, sig, t=None)

            a_xx = 0.5 * sig**2 / dx**2
            a_ss = 0.5 * p.eta**2 / ds**2
            bet  = p.beta * (p.sigma_bar - sig)

            # Upwind for σ-drift
            if bet >= 0:
                a_sp =  bet / ds;  a_sm = 0.0
            else:
                a_sp =  0.0;       a_sm = -bet / ds

            if mu >= 0:
                a_xp = mu / dx;  a_xm = 0.0   # upwind forward
            else:
                a_xp = 0.0;      a_xm = -mu / dx  # upwind backward

            # Diagonal  (negative of generator = positive definite system)
            A[row, row] = 2*a_xx + a_xp + a_xm + a_sp + a_sm + 2*a_ss + p.r_kill

            if xi - 1 == 0:          # left BC: u=0 at SL
                b[row] += (a_xx + a_xm) * 0.0
            else:
                A[row, idx(i-1, j)] -= (a_xx + a_xm)

            if xi + 1 == p.Nx - 1:  # right BC: u=1 at TP
                b[row] += (a_xx + a_xp) * 1.0
            else:
                A[row, idx(i+1, j)] -= (a_xx + a_xp)

            # σ neighbours with Neumann BC (reflect at boundaries)
            j_up = j + 1 if j < Nj - 1 else j - 1
            j_dn = j - 1 if j > 0      else j + 1

            A[row, idx(i, j_up)] -= a_ss + a_sp
            A[row, idx(i, j_dn)] -= a_ss + a_sm

            # Mixed derivative ρ σ η u_xσ  (central differences)
            if j > 0 and j < Nj - 1:
                coeff_mix = p.rho * sig * p.eta / (4 * dx * ds)

                if xi + 1 <= p.Nx - 2:
                    A[row, idx(i+1, j+1)] -= coeff_mix
                else:
                    b[row] += coeff_mix * 1.0

                if xi + 1 <= p.Nx - 2:
                    A[row, idx(i+1, j-1)] += coeff_mix
                else:
                    b[row] -= coeff_mix * 1.0

                if xi - 1 >= 1:
                    A[row, idx(i-1, j+1)] += coeff_mix
                else:
                    b[row] -= coeff_mix * 0.0

                if xi - 1 >= 1:
                    A[row, idx(i-1, j-1)] -= coeff_mix
                else:
                    b[row] += coeff_mix * 0.0

    print("  Solving sparse system …", end=" ")
    from scipy.sparse import csr_matrix
    u_flat = spsolve(csr_matrix(A), b)
    print("done.")

    # Reconstruct full grid (including boundaries)
    u = np.zeros((p.Nx, p.Ns))
    u[0,  :] = 0.0   # SL
    u[-1, :] = 1.0   # TP
    for i in range(Ni):
        for j in range(Nj):
            u[i+1, j] = u_flat[idx(i, j)]

    # Clip to [0,1] (small numerical violations possible near boundaries)
    u = np.clip(u, 0.0, 1.0)

    return u, x_grid, s_grid


# ══════════════════════════════════════════════════════════════════════════════
# 3.  DIAGNOSTICS FROM MC
# ══════════════════════════════════════════════════════════════════════════════

def mc_diagnostics(exit_val, exit_time, p: Params):
    tp_hits = np.sum(exit_val == p.TP)
    sl_hits = np.sum(exit_val == p.SL)
    no_exit = np.sum(np.isnan(exit_val))
    total   = len(exit_val)

    p_tp = tp_hits / total
    p_sl = sl_hits / total
    p_no = no_exit / total

    tp_times = exit_time[exit_val == p.TP]
    sl_times = exit_time[exit_val == p.SL]

    print(f"\n{'─'*50}")
    print(f"  Monte Carlo Results  (N={total})")
    print(f"{'─'*50}")
    print(f"  P(hit TP)       = {p_tp:.4f}  ({tp_hits} paths)")
    print(f"  P(hit SL)       = {p_sl:.4f}  ({sl_hits} paths)")
    print(f"  P(no exit by T) = {p_no:.4f}  ({no_exit} paths)")
    if len(tp_times) > 0:
        print(f"  Mean exit time | TP  = {tp_times.mean():.4f}")
        print(f"  Mean exit time | SL  = {sl_times.mean():.4f}" if len(sl_times) > 0 else "")
    exp_pnl = p_tp * p.TP + p_sl * p.SL
    print(f"  Expected P&L        = {exp_pnl:.4f}")
    print(f"{'─'*50}\n")

    return dict(p_tp=p_tp, p_sl=p_sl, p_no=p_no,
                tp_times=tp_times, sl_times=sl_times,
                exp_pnl=exp_pnl)


# ══════════════════════════════════════════════════════════════════════════════
# 4.  SENSITIVITY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def sensitivity_analysis(p: Params):
    """Vary σ₀, β, η, ρ one at a time and record P(TP)."""

    results = {}

    # vary sigma0
    sig0_vals = np.linspace(0.2, 2.5, 12)
    p_tp_sig0 = []
    for s0 in sig0_vals:
        p2 = Params(); p2.sigma0 = s0; p2.N_paths = 600; p2.seed = 1
        _, _, ev, _ = run_monte_carlo(p2)
        p_tp_sig0.append(np.mean(ev == p2.TP))
    results["sigma0"] = (sig0_vals, np.array(p_tp_sig0))

    # vary beta
    beta_vals = np.linspace(0.2, 6.0, 12)
    p_tp_beta = []
    for b in beta_vals:
        p2 = Params(); p2.beta = b; p2.N_paths = 600; p2.seed = 2
        _, _, ev, _ = run_monte_carlo(p2)
        p_tp_beta.append(np.mean(ev == p2.TP))
    results["beta"] = (beta_vals, np.array(p_tp_beta))

    # vary eta (vol-of-vol)
    eta_vals = np.linspace(0.05, 1.5, 12)
    p_tp_eta = []
    for e in eta_vals:
        p2 = Params(); p2.eta = e; p2.N_paths = 600; p2.seed = 3
        _, _, ev, _ = run_monte_carlo(p2)
        p_tp_eta.append(np.mean(ev == p2.TP))
    results["eta"] = (eta_vals, np.array(p_tp_eta))

    # vary rho
    rho_vals = np.linspace(-0.9, 0.9, 12)
    p_tp_rho = []
    for r in rho_vals:
        p2 = Params(); p2.rho = r; p2.N_paths = 600; p2.seed = 4
        _, _, ev, _ = run_monte_carlo(p2)
        p_tp_rho.append(np.mean(ev == p2.TP))
    results["rho"] = (rho_vals, np.array(p_tp_rho))

    # vary TP/SL ratio
    rr_vals = np.linspace(0.5, 4.0, 12)
    p_tp_rr = []
    for rr in rr_vals:
        p2 = Params(); p2.TP = rr * abs(p.SL); p2.N_paths = 600; p2.seed = 5
        _, _, ev, _ = run_monte_carlo(p2)
        p_tp_rr.append(np.mean(ev == p2.TP))
    results["rr"] = (rr_vals, np.array(p_tp_rr))

    return results


# ══════════════════════════════════════════════════════════════════════════════
# 5.  MASTER PLOT
# ══════════════════════════════════════════════════════════════════════════════

def plot_all(paths_x, paths_sig, exit_val, exit_time,
             diag, u_pde, x_grid, s_grid, sens, p: Params,
             save_path="cfd_sde_dashboard.png"):

    fig = plt.figure(figsize=(30, 38))
    fig.patch.set_facecolor(BG)

    fig.text(0.5, 0.995,
             "CFD FIRST-PASSAGE  ·  Stochastic Volatility SDE  ·  TP/SL Boundary Problem",
             ha="center", va="top", color=ACCENT, fontsize=15,
             fontweight="bold", fontfamily="monospace")
    fig.text(0.5, 0.991,
             f"dX = σ dW¹   |   dσ = β(σ̄−σ)dt + η dW²   |   ρ={p.rho}   "
             f"β={p.beta}  σ̄={p.sigma_bar}  η={p.eta}  TP={p.TP}  SL={p.SL}",
             ha="center", va="top", color=TMID, fontsize=8.5, fontfamily="monospace")

    outer = gridspec.GridSpec(5, 1, figure=fig,
                              top=0.988, bottom=0.01,
                              hspace=0.38, left=0.05, right=0.97)

    # ── ROW 0: Sample paths ─────────────────────────────────────────────────
    r0 = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=outer[0],
                                          wspace=0.3)

    # X paths — colour by outcome
    ax = fig.add_subplot(r0[0])
    steps    = paths_x.shape[1]
    t_axis   = np.linspace(0, p.T, steps)
    n_show   = min(300, p.N_paths)
    idx_show = np.random.choice(p.N_paths, n_show, replace=False)

    for i in idx_show:
        row = paths_x[i]
        valid = ~np.isnan(row)
        tv = t_axis[valid]; xv = row[valid]
        col = ACC3 if exit_val[i] == p.TP else \
              DANGER if exit_val[i] == p.SL else TMID
        ax.plot(tv, xv, color=col, lw=0.35, alpha=0.35)

    ax.axhline(p.TP, color=ACC3,  lw=1.5, ls="--", label=f"TP={p.TP}")
    ax.axhline(p.SL, color=DANGER,lw=1.5, ls="--", label=f"SL={p.SL}")
    ax.axhline(0,    color=LGREY, lw=0.8, ls=":",  alpha=0.6)
    ax.legend(fontsize=7, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _sax(ax, f"X_t Paths (green=TP hit, red=SL hit, n={n_show})", "time", "X_t")

    # σ paths
    ax2 = fig.add_subplot(r0[1])
    for i in idx_show[:150]:
        row = paths_sig[i]
        valid = ~np.isnan(row)
        ax2.plot(t_axis[valid], row[valid],
                 color=ACCENT, lw=0.3, alpha=0.25)
    ax2.axhline(p.sigma_bar, color=WARN, lw=1.2, ls="--", label=f"σ̄={p.sigma_bar}")
    ax2.legend(fontsize=7, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _sax(ax2, "σ_t Paths (stochastic vol)", "time", "σ_t")

    # Exit time distribution
    ax3 = fig.add_subplot(r0[2])
    tp_t = diag["tp_times"]; sl_t = diag["sl_times"]
    bins = np.linspace(0, p.T, 60)
    if len(tp_t): ax3.hist(tp_t, bins=bins, color=ACC3,  alpha=0.7,
                            label=f"TP exits ({len(tp_t)})", density=True)
    if len(sl_t): ax3.hist(sl_t, bins=bins, color=DANGER, alpha=0.7,
                            label=f"SL exits ({len(sl_t)})", density=True)
    ax3.legend(fontsize=7, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _sax(ax3, "Exit Time Distribution", "exit time", "density")

    # ── ROW 1: Phase-space and vol scatter ──────────────────────────────────
    r1 = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=outer[1], wspace=0.3)

    # Joint (X, σ) scatter at exit
    ax4 = fig.add_subplot(r1[0])
    tp_mask = exit_val == p.TP
    sl_mask = exit_val == p.SL

    # Get σ at exit time for each path
    def sig_at_exit(paths_sig, exit_time, dt):
        out = np.full(len(exit_time), np.nan)
        for i, et in enumerate(exit_time):
            if not np.isnan(et):
                idx_ = int(round(et / dt))
                idx_ = min(idx_, paths_sig.shape[1] - 1)
                out[i] = paths_sig[i, idx_]
        return out

    sig_exit = sig_at_exit(paths_sig, exit_time, p.dt)
    ax4.scatter(exit_time[tp_mask], sig_exit[tp_mask],
                color=ACC3,  s=4, alpha=0.5, label="TP exits")
    ax4.scatter(exit_time[sl_mask], sig_exit[sl_mask],
                color=DANGER, s=4, alpha=0.5, label="SL exits")
    ax4.legend(fontsize=7, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _sax(ax4, "Exit Time vs σ at Exit", "exit time", "σ at exit")

    # σ distribution at different time slices
    ax5 = fig.add_subplot(r1[1])
    slice_times = [0.1, 0.3, 0.5, 0.8]
    s_colors    = [ACCENT, ACC2, ACC3, ACC4]
    for st, sc in zip(slice_times, s_colors):
        idx_t = int(st / p.dt)
        sig_slice = paths_sig[:, min(idx_t, paths_sig.shape[1]-1)]
        sig_slice = sig_slice[~np.isnan(sig_slice)]
        if len(sig_slice) > 10:
            ax5.hist(sig_slice, bins=40, color=sc, alpha=0.5,
                     label=f"t={st}", density=True)
    ax5.axvline(p.sigma_bar, color=WARN, lw=1.2, ls="--", label="σ̄")
    ax5.legend(fontsize=7, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _sax(ax5, "σ_t Distribution at Time Slices", "σ", "density")

    # Running P(TP) estimate as paths accumulate
    ax6 = fig.add_subplot(r1[2])
    sorted_exits = np.sort(exit_time[~np.isnan(exit_time)])
    tp_running = []; sl_running = []; t_running = []
    cum_tp = 0; cum_sl = 0
    for i, et in enumerate(np.sort(exit_time)):
        if np.isnan(et): continue
        path_idx = np.argsort(exit_time)[i]
        if exit_val[path_idx] == p.TP: cum_tp += 1
        else: cum_sl += 1
        total_done = cum_tp + cum_sl
        if total_done % 20 == 0:
            tp_running.append(cum_tp / p.N_paths)
            sl_running.append(cum_sl / p.N_paths)
            t_running.append(et)

    if t_running:
        ax6.plot(t_running, tp_running, color=ACC3,  lw=1.2, label="P(TP) running")
        ax6.plot(t_running, sl_running, color=DANGER, lw=1.2, label="P(SL) running")
        ax6.axhline(diag["p_tp"], color=ACC3,  lw=0.7, ls=":", alpha=0.8)
        ax6.axhline(diag["p_sl"], color=DANGER, lw=0.7, ls=":", alpha=0.8)
    ax6.legend(fontsize=7, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _sax(ax6, "Running Probability Estimates", "time", "probability")

    # ── ROW 2: PDE solution ──────────────────────────────────────────────────
    r2 = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=outer[2], wspace=0.32)

    # 2D heatmap of u(x, σ)
    ax7 = fig.add_subplot(r2[0])
    u_smooth = u_pde #gaussian_filter(u_pde, sigma=0.8)
    im = ax7.imshow(u_smooth.T, origin="lower", aspect="auto",
                    extent=[p.SL, p.TP, s_grid[0], s_grid[-1]],
                    cmap=CMAP_PROB, vmin=0, vmax=1)
    cb = fig.colorbar(im, ax=ax7, fraction=0.04)
    cb.ax.tick_params(colors=TMID, labelsize=6)
    cb.set_label("P(hit TP)", color=TMID, fontsize=7)
    ax7.axvline(0, color=WARN, lw=0.8, ls="--", alpha=0.7, label="x=0")
    ax7.set_xlabel("X (position)", color=TMID, fontsize=7)
    ax7.set_ylabel("σ", color=TMID, fontsize=7)
    ax7.set_title("PDE: P(hit TP | X, σ)", color=TWHITE, fontsize=8,
                  fontweight="bold", pad=4)
    ax7.tick_params(colors=TMID, labelsize=7)
    for sp in ax7.spines.values(): sp.set_edgecolor(BORDER)

    # Contour plot
    ax8 = fig.add_subplot(r2[1])
    XX, SS = np.meshgrid(x_grid, s_grid, indexing="ij")
    levels = np.linspace(0, 1, 21)
    cs = ax8.contourf(XX, SS, u_smooth, levels=levels, cmap=CMAP_PROB)
    ct = ax8.contour(XX, SS, u_smooth,
                     levels=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9],
                     colors=TWHITE, linewidths=0.6, alpha=0.7)
    ax8.clabel(ct, fmt="%.1f", colors=TWHITE, fontsize=6)
    fig.colorbar(cs, ax=ax8, fraction=0.04).ax.tick_params(colors=TMID, labelsize=6)
    ax8.axvline(0, color=WARN, lw=0.8, ls="--", alpha=0.7)
    ax8.set_xlabel("X", color=TMID, fontsize=7)
    ax8.set_ylabel("σ", color=TMID, fontsize=7)
    ax8.set_title("Contour: P(TP) Iso-probability Lines", color=TWHITE,
                  fontsize=8, fontweight="bold", pad=4)
    ax8.tick_params(colors=TMID, labelsize=7)
    for sp in ax8.spines.values(): sp.set_edgecolor(BORDER)

    # Slices of u at fixed σ values
    ax9 = fig.add_subplot(r2[2])
    sig_slices  = np.linspace(0, p.sigma0, 5) #[0.3, 0.6, 1.0, 1.5, 2.2]
    sl_colors_p = [ACCENT, ACC2, ACC3, ACC4, WARN]
    for sv, sc in zip(sig_slices, sl_colors_p):
        j_idx = np.argmin(np.abs(s_grid - sv))
        ax9.plot(x_grid, u_pde[:, j_idx], color=sc, lw=1.2, label=f"σ={sv:.1f}")
    ax9.axvline(0, color=LGREY, lw=0.8, ls=":", alpha=0.7)
    ax9.axhline(0.5, color=LGREY, lw=0.6, ls="--", alpha=0.5)
    ax9.legend(fontsize=7, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _sax(ax9, "P(TP) vs Position  at Fixed σ", "X", "P(hit TP)")

    # ── ROW 3: PDE vs MC comparison + σ slices ──────────────────────────────
    r3 = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=outer[3], wspace=0.32)

    # PDE vs MC at σ=σ0
    ax10 = fig.add_subplot(r3[0])
    j0 = np.argmin(np.abs(s_grid - p.sigma0))

    # MC estimate of P(TP) at x0 binned
    x_bins = np.linspace(p.SL * 0.8, p.TP * 0.8, 25)
    mc_p_tp = []
    for xb in x_bins:
        # Paths that pass near xb at t=0.05 (early slice)
        t05 = int(0.05 / p.dt)
        x_at_t05 = paths_x[:, t05]
        mask_near = np.abs(x_at_t05 - xb) < (p.TP - p.SL) / 20
        if mask_near.sum() > 5:
            mc_p_tp.append(np.mean(exit_val[mask_near] == p.TP))
        else:
            mc_p_tp.append(np.nan)

    ax10.plot(x_grid, u_pde[:, j0], color=ACCENT, lw=1.5, label=f"PDE (σ={p.sigma0})")
    ax10.scatter(x_bins, mc_p_tp, color=ACC2, s=20, zorder=5, label="MC estimate")
    ax10.axvline(0,   color=LGREY, lw=0.8, ls=":", alpha=0.7)
    ax10.axhline(0.5, color=LGREY, lw=0.6, ls="--", alpha=0.5)
    ax10.legend(fontsize=7, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _sax(ax10, "PDE vs MC: P(TP) at σ=σ₀", "X", "P(hit TP)")

    # σ effect on P(TP) at x=0 (from PDE)
    ax11 = fig.add_subplot(r3[1])
    i_mid = np.argmin(np.abs(x_grid - 0))
    ax11.plot(s_grid, u_pde[i_mid, :], color=ACC3, lw=1.5, label="x=0")
    i_tp4 = np.argmin(np.abs(x_grid - p.TP/4))
    i_sl4 = np.argmin(np.abs(x_grid - p.SL/4))
    ax11.plot(s_grid, u_pde[i_tp4, :], color=ACCENT, lw=1.2, ls="--", label=f"x=+{p.TP/4:.0f}")
    ax11.plot(s_grid, u_pde[i_sl4, :], color=DANGER, lw=1.2, ls="--", label=f"x={p.SL/4:.0f}")
    ax11.axhline(0.5, color=LGREY, lw=0.6, ls=":", alpha=0.6)
    ax11.legend(fontsize=7, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
    _sax(ax11, "P(TP) vs σ  at Fixed Positions", "σ", "P(hit TP)")

    # 3D-style surface using pcolormesh with perspective trick
    ax12 = fig.add_subplot(r3[2], projection=None)
    # Derivative: ∂u/∂x  = sensitivity to price move (like delta)
    du_dx = np.gradient(u_pde, x_grid, axis=0)
    j_vals = [0, len(s_grid)//4, len(s_grid)//2, 3*len(s_grid)//4, -1]
    for j in j_vals:
        sig_val = s_grid[j]
        grad_slice = du_dx[:, j]
        print(f"sigma={sig_val:.2f}  |  "
            f"min={grad_slice.min():.4f}  "
            f"max={grad_slice.max():.4f}  "
            f"mean={grad_slice.mean():.4f}")

    du_dx = du_dx / (du_dx.mean(axis=1, keepdims=True) + 1e-9)

    vabs = np.percentile(np.abs(du_dx), 95)  # robust to outliers
    im2 = ax12.imshow(du_dx.T, origin="lower", aspect="auto",
                      extent=[p.SL, p.TP, s_grid[0], s_grid[-1]],
                      cmap=CMAP_VOL, vmin=0, vmax=vabs)
    cb2 = fig.colorbar(im2, ax=ax12, fraction=0.04)
    cb2.ax.tick_params(colors=TMID, labelsize=6)
    cb2.set_label("∂P/∂X  (price sensitivity)", color=TMID, fontsize=7)
    ax12.set_xlabel("X", color=TMID, fontsize=7)
    ax12.set_ylabel("σ", color=TMID, fontsize=7)
    ax12.set_title("∂P(TP)/∂X  — Price Sensitivity (Delta)", color=TWHITE,
                   fontsize=8, fontweight="bold", pad=4)
    ax12.tick_params(colors=TMID, labelsize=7)
    for sp in ax12.spines.values(): sp.set_edgecolor(BORDER)

    # ── ROW 4: Sensitivity analysis ─────────────────────────────────────────
    r4 = gridspec.GridSpecFromSubplotSpec(1, 5, subplot_spec=outer[4], wspace=0.35)

    sens_defs = [
        ("sigma0", "Initial σ₀",     "σ₀",       ACCENT),
        ("beta",   "Mean-Rev Speed β","β",         ACC2),
        ("eta",    "Vol-of-Vol η",    "η",         ACC3),
        ("rho",    "Correlation ρ",   "ρ",         ACC4),
        ("rr",     "TP/|SL| Ratio",   "TP/|SL|",  WARN),
    ]

    for idx_, (key, title, xl, col) in enumerate(sens_defs):
        ax_ = fig.add_subplot(r4[idx_])
        xs, ys = sens[key]
        ax_.plot(xs, ys, color=col, lw=1.5, marker="o", ms=4,
                 markerfacecolor=SURF, markeredgecolor=col)
        ax_.fill_between(xs, ys, 0.5, alpha=0.15, color=col)
        ax_.axhline(0.5, color=LGREY, lw=0.8, ls="--", alpha=0.7, label="P=0.5")
        ax_.set_ylim(0, 1)
        ax_.legend(fontsize=6, facecolor=SURF2, edgecolor=BORDER, labelcolor=TWHITE)
        _sax(ax_, f"Sensitivity: {title}", xl, "P(hit TP)")

    # ── Summary text box ─────────────────────────────────────────────────────
    summary = (
        f"  RESULTS SUMMARY\n"
        f"  ─────────────────────────────────────\n"
        f"  P(hit TP)        =  {diag['p_tp']:.4f}\n"
        f"  P(hit SL)        =  {diag['p_sl']:.4f}\n"
        f"  P(no exit by T)  =  {diag['p_no']:.4f}\n"
        f"  Expected P&L     =  {diag['exp_pnl']:.4f}\n"
        f"  ─────────────────────────────────────\n"
        f"  TP = {p.TP}  |  SL = {p.SL}\n"
        f"  σ₀={p.sigma0}  β={p.beta}  σ̄={p.sigma_bar}  η={p.eta}  ρ={p.rho}\n"
        f"  N={p.N_paths} paths  dt={p.dt}  T={p.T}"
    )
    fig.text(0.73, 0.028, summary, color=TWHITE, fontsize=8,
             fontfamily="monospace", va="bottom",
             bbox=dict(boxstyle="round,pad=0.6", facecolor=SURF2,
                       edgecolor=ACCENT, alpha=0.9))

    plt.savefig(save_path, dpi=120, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"✔  Dashboard saved → {save_path}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def sweep_boundaries(p, mu_M, sigma_current,
                     tp_multiples=np.linspace(0.1, 5, 10),
                     sl_multiples=np.linspace(0.1, 5, 10)):
    """
    For each (TP, SL) combination expressed as vol multiples,
    compute E[PnL | x=0, sigma=sigma_current] under model M.
    
    Returns a 2D surface of expected PnL over TP/SL space.
    This tells you which boundary placements give positive edge
    under your current model and vol regime.
    """
    results = np.zeros((len(tp_multiples), len(sl_multiples)))
    
    for i, tp_mult in enumerate(tp_multiples):
        for j, sl_mult in enumerate(sl_multiples):
            p_sweep      = Params()
            p_sweep.TP   =  tp_mult * sigma_current
            p_sweep.SL   = -sl_mult * sigma_current
            p_sweep.sigma0    = sigma_current
            p_sweep.sigma_bar = p.sigma_bar
            p_sweep.eta       = p.eta
            p_sweep.beta      = p.beta
            p_sweep.rho       = p.rho
            p_sweep.r_kill    = p.r_kill
            p_sweep.mu_fn     = lambda x,s,t: np.full_like(x, mu_M)
            
            u, x_grid, s_grid = solve_pde(p_sweep)
            
            i0   = np.argmin(np.abs(x_grid - 0))
            j0   = np.argmin(np.abs(s_grid - sigma_current))
            p_tp = u[i0, j0]
            
            E_pnl = p_tp * p_sweep.TP + (1-p_tp) * p_sweep.SL
            results[i, j] = E_pnl
            print(f"TP_mult={tp_mult:.2f}  SL_mult={sl_mult:.2f}",
                  f"P(TP)={p_tp:.4f}  E[PnL]={E_pnl:.4f}")
    
    return results, tp_multiples, sl_multiples



if __name__ == "__main__":
    p = Params()

    print("=" * 55)
    print("  CFD First-Passage Time  —  Stochastic Vol SDE")
    print("=" * 55)
    print(f"  TP={p.TP}  SL={p.SL}  σ₀={p.sigma0}")
    print(f"  β={p.beta}  σ̄={p.sigma_bar}  η={p.eta}  ρ={p.rho}")
    print(f"  N_paths={p.N_paths}  dt={p.dt}  T={p.T}")
    print("=" * 55)

    print("\n[1/4] Running Monte Carlo …")
    paths_x, paths_sig, exit_val, exit_time = run_monte_carlo(p, x0=0.0)
    diag = mc_diagnostics(exit_val, exit_time, p)

    print("[2/4] Solving PDE (Kolmogorov backward equation) …")
    u_pde, x_grid, s_grid = solve_pde(p)

    # PDE-based probability at (x=0, σ=σ0)
    i0 = np.argmin(np.abs(x_grid - 0))
    j0 = np.argmin(np.abs(s_grid - p.sigma0))
    print(f"\n  PDE P(TP | x=0, σ={p.sigma0}) = {u_pde[i0, j0]:.4f}")
    print(f"  MC  P(TP | x=0)              = {diag['p_tp']:.4f}")

    print("\n[3/4] Running sensitivity analysis …")
    sens = sensitivity_analysis(p)

    print("\n[4/4] Plotting dashboard …")
    plot_all(paths_x, paths_sig, exit_val, exit_time,
             diag, u_pde, x_grid, s_grid, sens, p,
             save_path="Simulations/cfd_sde_dashboard.png")
    
    u_model, _, _          = solve_pde(p)
    p.mu_fn = lambda x,s,t: np.full_like(x, 0.0)  # null model with zero drift
    u_null, x_grid, s_grid = solve_pde(p)

    i0 = np.argmin(np.abs(x_grid))
    j0 = np.argmin(np.abs(s_grid - p.sigma0))

    p_null  = u_null[i0, j0]
    p_model = u_model[i0, j0]
    edge    = p_model - p_null

    # MC confidence interval on the null
    n       = 3000
    se_mc   = np.sqrt(p_null * (1-p_null) / n)
    z       = edge / se_mc

    print(f"P(TP) null  : {p_null:.4f}")
    print(f"P(TP) model : {p_model:.4f}")
    print(f"Edge        : {edge:.4f}")
    print(f"MC SE       : {se_mc:.4f}")
    print(f"Z-score     : {z:.2f}")
    print(f"Significant : {abs(z) > 1.96}")

    results, tp_m, sl_m = sweep_boundaries(p, mu_M=p.mu, 
                                        sigma_current=p.sigma0)

    plt.figure(figsize=(10, 8))
    plt.contourf(sl_m, tp_m, results, levels=20, cmap='RdYlGn')
    plt.colorbar(label='E[PnL]')
    plt.contour(sl_m, tp_m, results, levels=[0], 
                colors='black', linewidths=2)
    plt.xlabel('SL multiple of sigma')
    plt.ylabel('TP multiple of sigma')
    plt.title('Expected PnL across TP/SL space\n'
            f'sigma={p.sigma0:.1f}, mu_M={p.mu}')
    plt.axvline(-p.SL/p.sigma0, color='red', ls='--', 
                label=f'current SL={p.SL}pts')
    plt.axhline(p.TP/p.sigma0, color='red', ls='--',
                label=f'current TP={p.TP}pts')
    plt.legend()
    plt.savefig("Simulations/cfd_sde_tp_sl_sweep.png", dpi=120, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.show()
