from abc import ABC, abstractmethod
import numpy as np
import pandas as pd

class BaseModel(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Batch prediction over full DataFrame.
        Returns np.ndarray of length len(df).
        NaN where insufficient history.
        Called once per backtest run.
        """

    @abstractmethod
    def update(self, df: pd.DataFrame) -> float:
        """
        Incremental single-bar update for live MT5 loop.
        df is the full DataFrame with the new bar appended.
        Returns single float — mu estimate for the latest bar.
        """