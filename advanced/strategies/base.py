from abc import ABC, abstractmethod
from .data_structures import EntryFeatures, EntryDecision

class Strategy(ABC):
    @abstractmethod
    def __call__(self, features: EntryFeatures,
                 config: dict={}) -> EntryDecision:
        """
        Fixed IO — EntryFeatures in, EntryDecision out.
        config dict contains all thresholds and flags
        for this strategy. The grid search sweeps over
        different config dicts.
        """