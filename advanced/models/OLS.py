import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
from .model import BaseModel

def latest_slope(prices: np.ndarray, window: int = 10) -> float:
    if len(prices) < window:
        print("Not enough data to compute slope. Returning NaN.")
        return np.nan

    y = prices[-window:]
    x = np.arange(window, dtype=float)
    xm = x.mean()
    ym = y.mean()
    cov = np.sum((x - xm) * (y - ym))
    var = np.sum((x - xm) ** 2)

    if var < 1e-12:
        print("Variance is too small to compute slope. Returning NaN.")
        return np.nan

    return cov / var

def compute_forward_slope(prices: np.ndarray, window: int = 10) -> np.ndarray:
    n = len(prices)
    slopes = np.full(n, np.nan)

    if n < window:
        return slopes

    Y = sliding_window_view(prices, window_shape=window)
    x = np.arange(window, dtype=float)
    xm = x.mean()
    denom = np.sum((x - xm) ** 2)

    if denom < 1e-12:
        return slopes

    Ym = Y.mean(axis=1)
    cov = np.sum((x - xm) * (Y - Ym[:, None]), axis=1)
    s = cov / denom
    slopes[: n - window] = s[: n - window]

    return slopes

class OLSModel(BaseModel):
    def __init__(self, window: int = 10, column: str = "close"):
        super().__init__()
        self.window = window
        self.column = column

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        return compute_forward_slope(df[self.column].values, window=self.window)

    def update(self, df: pd.DataFrame) -> float:
        return latest_slope(df[self.column].values, window=self.window)