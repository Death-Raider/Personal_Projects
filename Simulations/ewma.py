import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def compute_ewma_vol(returns, lambda_=0.94):
    """
    Compute EWMA volatility series.
    returns: log returns (pd.Series)
    """
    var = np.zeros(len(returns))
    var[0] = returns.var()

    for t in range(1, len(returns)):
        var[t] = (
            lambda_ * var[t-1]
            + (1 - lambda_) * returns.iloc[t-1]**2
        )

    return np.sqrt(var)


def monte_carlo_ewma(
    price_series,
    T=20,                # forecast horizon (days)
    steps_per_day=1,
    n_paths=5000,
    lambda_=0.94,
    S0=None,
    TP=None,
    SL=None
):
    """
    Monte Carlo simulation using EWMA volatility.
    Drift = 0.
    """

    log_returns = np.log(price_series / price_series.shift(1)).dropna()

    # Estimate EWMA volatility
    ewma_vol = compute_ewma_vol(log_returns, lambda_)
    sigma_t = ewma_vol[-1]  # start from latest volatility
    

    if S0 is None:
        S0 = price_series.iloc[-1]

    dt = 1 / 252 / steps_per_day
    total_steps = int(T * steps_per_day)

    paths = np.zeros((n_paths, total_steps))
    paths[:, 0] = S0

    barrier_results = []

    for i in range(1, total_steps):
        Z = np.random.normal(0, 1, n_paths)

        sigma_t = np.sqrt(
            lambda_ * sigma_t**2
            + (1 - lambda_) * (np.sqrt(dt) * Z.mean())**2
        )

        # simulate next step (mu = 0)
        paths[:, i] = paths[:, i-1] * np.exp(
            (-0.5 * sigma_t**2) * dt
            + sigma_t * np.sqrt(dt) * Z
        )

        # Optional barrier logic
        if TP is not None or SL is not None:
            for j in range(n_paths):
                if TP is not None and paths[j, i] >= TP:
                    barrier_results.append("TP")
                elif SL is not None and paths[j, i] <= SL:
                    barrier_results.append("SL")

    return paths

S0 = 100
total_steps = 1000
dt = 1 / 252

mu = 0.2      # annual drift (15%)
sigma = 0.6    # annual volatility (90%)

prices = np.zeros(total_steps)
prices[0] = S0

for t in range(1, total_steps):
    Z = np.random.normal(0, 1)
    prices[t] = prices[t-1] * np.exp(
        (mu - 0.5 * sigma**2) * dt
        + sigma * np.sqrt(dt) * Z
    )

price_series = pd.Series(prices, name="price")

paths = monte_carlo_ewma(
    price_series=price_series,
    T=20,
    n_paths=5000,
    lambda_=0.90,
    S0=prices[-1],
    TP=12000,
    SL=9000
)
S0 = price_series.iloc[-1]
terminal_prices = paths[:, -1]
prob_up = np.mean(terminal_prices > S0)
expected_return = np.mean(terminal_prices - S0)

percentile_5 = np.percentile(paths, 5, axis=0)
percentile_50 = np.percentile(paths, 50, axis=0)
percentile_95 = np.percentile(paths, 95, axis=0)

print(f"Estimated Probability of Price Increase: {prob_up:.4f}")
print(f"Estimated Expected Return: {expected_return:.4f}")


plt.figure(figsize=(10,6))

t = np.arange(paths.shape[1])
plt.plot(t, percentile_50, label="Median Forecast")
plt.fill_between(
    t,
    percentile_5,
    percentile_95,
    alpha=0.5,
    label="90% Cone"
)

plt.plot(t, paths[:1000].T, alpha=0.1)
plt.title("Monte Carlo Paths (Time-Dependent μ and σ)")
plt.show()


plt.figure(figsize=(12,6))
k = 150
plt.plot(range(k), price_series.values[-k:], label="Historical Price")
future_index = np.arange(len(price_series.index[-k:]), len(price_series.index[-k:]) + paths.shape[1])-1
plt.plot(future_index, percentile_50, label="Median Forecast")

plt.fill_between(
    future_index,
    percentile_5,
    percentile_95,
    alpha=0.3,
    label="90% Cone"
)

plt.legend()
plt.title("Price Forecast Cone")
plt.show()