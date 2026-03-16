from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import spsolve
import numpy as np

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

def solve_pde(p, mu=0.0):
    x_grid = np.linspace(p.SL, p.TP,       p.Nx)
    s_grid = np.linspace(1e-3, p.sigma_max, p.Ns)
    dx     = x_grid[1] - x_grid[0]
    ds     = s_grid[1] - s_grid[0]
    Ni     = p.Nx - 2
    Nj     = p.Ns
    N      = Ni * Nj

    def idx(i, j): return i * Nj + j

    A = lil_matrix((N, N))
    b = np.zeros(N)

    for i in range(Ni):
        xi = i + 1
        for j in range(Nj):
            sig = s_grid[j]
            row = idx(i, j)
            bet = p.beta * (p.sigma_bar - sig)

            a_xx = 0.5 * sig**2   / dx**2
            a_ss = 0.5 * p.eta**2 / ds**2

            if mu >= 0: a_xp = mu / dx;   a_xm = 0.0
            else:       a_xp = 0.0;        a_xm = -mu / dx

            if bet >= 0: a_sp = bet / ds;  a_sm = 0.0
            else:        a_sp = 0.0;       a_sm = -bet / ds

            A[row, row] = (2*a_xx + a_xp + a_xm +
                           2*a_ss + a_sp + a_sm + p.r_kill)

            if xi - 1 == 0:          b[row] += (a_xx + a_xm) * 0.0
            else: A[row, idx(i-1,j)] -= (a_xx + a_xm)

            if xi + 1 == p.Nx - 1:  b[row] += (a_xx + a_xp) * 1.0
            else: A[row, idx(i+1,j)] -= (a_xx + a_xp)

            j_up = j+1 if j < Nj-1 else j-1
            j_dn = j-1 if j > 0    else j+1
            A[row, idx(i, j_up)] -= (a_ss + a_sp)
            A[row, idx(i, j_dn)] -= (a_ss + a_sm)

            if j > 0 and j < Nj - 1:
                cm = p.rho * sig * p.eta / (4 * dx * ds)
                if xi+1 <= p.Nx-2: A[row, idx(i+1, j+1)] -= cm
                else:               b[row] += cm * 1.0
                if xi+1 <= p.Nx-2: A[row, idx(i+1, j-1)] += cm
                else:               b[row] -= cm * 1.0
                if xi-1 >= 1:      A[row, idx(i-1, j+1)] += cm
                if xi-1 >= 1:      A[row, idx(i-1, j-1)] -= cm

    u_flat = spsolve(csr_matrix(A), b)
    u      = np.zeros((p.Nx, p.Ns))
    u[0,:] = 0.0;  u[-1,:] = 1.0
    for i in range(Ni):
        for j in range(Nj):
            u[i+1, j] = u_flat[idx(i, j)]

    return np.clip(u, 0, 1), x_grid, s_grid