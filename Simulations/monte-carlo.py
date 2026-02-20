import numpy as np
import matplotlib.pyplot as plt

def monte_carlo_time_dependent(
    S0=100,
    T=1.0,
    steps=252,
    n_paths=5000,
    mu_func=None,
    sigma_func=None
):
    dt = T / steps
    t_grid = np.linspace(0, T, steps)
    
    paths = np.zeros((n_paths, steps))
    paths[:, 0] = S0
    
    for i in range(1, steps):
        t = t_grid[i]
        
        mu_t = mu_func(t)
        sigma_t = sigma_func(t)
        
        Z = np.random.normal(0, 1, n_paths)
        
        paths[:, i] = paths[:, i-1] * np.exp(
            (mu_t - 0.5 * sigma_t**2) * dt
            + sigma_t * np.sqrt(dt) * Z
        )
    
    return t_grid, paths

def mu_func(t):
    return 0.05 + 0.03 * np.sin(4 * np.pi * t)

def sigma_func(t):
    return 0.2 + 0.1 * np.cos(4 * np.pi * t)

t, paths = monte_carlo_time_dependent(
    S0=100,
    T=20,
    steps=1000,
    n_paths=2,
    mu_func=mu_func,
    sigma_func=sigma_func
)

plt.figure(figsize=(10,6))
plt.plot(t, paths[:50].T)
plt.title("Monte Carlo Paths (Time-Dependent μ and σ)")
plt.show()