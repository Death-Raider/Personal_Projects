import numpy as np
import pandas as pd
from scipy.optimize import minimize
import matplotlib.pyplot as plt

def compute_garch_variance(returns, omega, alpha, beta):
    T = len(returns)
    var = np.zeros(T)
    var[0] = np.var(returns)

    for t in range(1, T):
        var[t] = omega + alpha * returns[t-1]**2 + beta * var[t-1]

    return var

def estimate_garch_params(returns):
    """
    Estimate GARCH(1,1) parameters via simple likelihood minimization.
    """

    returns = returns.values
    T = len(returns)

    def garch_likelihood(params):
        omega, alpha, beta = params

        if omega <= 0 or alpha < 0 or beta < 0 or alpha + beta >= 1:
            return 1e10

        var = compute_garch_variance(returns, omega, alpha, beta)

        loglik = -0.5 * np.sum(
            np.log(2 * np.pi)
            + np.log(var)
            + returns**2 / var
        )

        return -loglik

    initial_guess = [1e-6, 0.05, 0.9]

    result = minimize(
        garch_likelihood,
        initial_guess,
        bounds=[(1e-10, None), (0, 1), (0, 1)]
    )

    return result.x

def monte_carlo_garch(
    price_series,
    T=20,               # forecast horizon (days)
    n_paths=5000
):
    log_returns = np.log(price_series / price_series.shift(1)).dropna()

    omega, alpha, beta = estimate_garch_params(log_returns)

    last_return = log_returns.iloc[-1]
    last_var = var = compute_garch_variance(log_returns.values, omega, alpha, beta)[-1]

    S0 = price_series.iloc[-1]

    dt = 1 / 252
    steps = T

    paths = np.zeros((n_paths, steps))
    paths[:, 0] = S0

    for j in range(n_paths):

        S = S0
        var = last_var
        r_prev = last_return

        for t in range(1, steps):

            # Update variance
            var = omega + alpha * r_prev**2 + beta * var
            sigma = np.sqrt(var)

            # Draw shock
            Z = np.random.normal()
            # Z = np.random.standard_t(df=5)

            # Generate return
            r = sigma * Z

            # Update price
            S = S * np.exp(r)

            paths[j, t] = S

            r_prev = r

    return paths


S0 = 100
total_steps = 100
dt = 1 / 252
sigma = 0.2

prices = np.zeros(total_steps)
prices[0] = S0
for t in range(1, total_steps):
    Z = np.random.normal(0, 1)
    prices[t] = prices[t-1] * np.exp(
        sigma * np.sqrt(dt) * Z
    )
price_series = pd.Series(prices.tolist(), name="price")

paths = monte_carlo_garch(
    price_series=price_series,
    T=5,
    n_paths=5000,

)

terminal_prices = paths[:, -1]
prob_up = np.mean(terminal_prices > S0)
expected_return = np.mean(terminal_prices - S0)

print(f"Estimated Probability of Price Increase: {prob_up:.4f}")
print(f"Estimated Expected Return: {expected_return:.4f}")

plt.figure(figsize=(10,6))
t = np.arange(paths.shape[1])
plt.plot(t, paths[:1000].T)
plt.title("Monte Carlo Paths (Time-Dependent μ and σ)")
plt.show()