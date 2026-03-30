import numpy as np
import pandas as pd
from .model import BaseModel

def latest_mu_mle(prices: np.ndarray, sigma_series: np.ndarray,window: int = 50) -> float:
    """Single-bar live update — mirrors latest_slope."""
    if len(prices) < window + 1:
        return np.nan
    dx  = np.diff(prices[-window-1:])
    sig = sigma_series[-window:]
    w   = 1.0 / (sig**2 + 1e-9)
    return float(np.sum(w * dx) / (np.sum(w) + 1e-9))


def compute_mu_mle(prices: np.ndarray, sigma_series: np.ndarray,window: int = 50) -> np.ndarray:
    """Historical batch — mirrors compute_forward_slope."""
    n      = len(prices)
    mu_arr = np.full(n, np.nan)
    dx     = np.diff(prices)
    for t in range(window, n):
        dx_w  = dx[t-window:t]
        sig_w = sigma_series[t-window:t]
        w     = 1.0 / (sig_w**2 + 1e-9)
        mu_arr[t] = np.sum(w * dx_w) / (np.sum(w) + 1e-9)

    for row in range(n - window, n):
        if np.isnan(mu_arr[row]):
            mu_arr[row] = latest_mu_mle(
                prices[max(0, row-window-1):row+1],
                sigma_series[max(0, row-window):row+1],
                window=window
            )
    return mu_arr

class MLEModel(BaseModel):
    def __init__(self, window: int = 10, column: str = "close"):
        super().__init__()
        self.window = window
        self.column = column

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        ss = df[self.column].diff().rolling(window=self.window).std().values
        return compute_mu_mle(df[self.column].values, sigma_series=ss, window=self.window)

    def update(self, df: pd.DataFrame) -> float:
        ss = df[self.column].diff().rolling(window=self.window).std().values
        return latest_mu_mle(df[self.column].values, sigma_series=ss, window=self.window)