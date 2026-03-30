from .data_structures import EntryFeatures, EntryDecision
from .base import Strategy

class AlwaysBuyStrategy(Strategy):
    
    def __init__(self):
        pass

    def __call__(self, features: EntryFeatures,
                 config: dict={}) -> EntryDecision:
        return EntryDecision(
            enter       = True,
            direction   = "long",
            reason      = "null — always enter",
            p_tp_entry  = features.p_tp_entry,
            edge        = features.edge_long,
            vol_ratio   = features.vol_ratio,
        )