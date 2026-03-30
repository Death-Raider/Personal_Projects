from .data_structures import EntryFeatures, EntryDecision
from .base import Strategy

class PDEEdgeStrategy(Strategy):
    
    def __init__(self):
        pass

    def __call__(self, features: EntryFeatures,
                 config: dict={}) -> EntryDecision:
        
        EDGE_THRESHOLD_LONG = config.get("edge_threshold_long", 0.05)
        EDGE_THRESHOLD_SHORT = config.get("edge_threshold_short", 0.05)

        if features.edge_long > EDGE_THRESHOLD_LONG:
            return EntryDecision(enter=True, direction="long",
                        reason=f"long edge={features.edge_long:.3f}",
                        p_tp_entry=features.p_tp_entry, edge=features.edge_long,
                        vol_ratio=features.vol_ratio)
        elif features.edge_short > EDGE_THRESHOLD_SHORT:
            return EntryDecision(enter=True, direction="short",
                        reason=f"short edge={features.edge_short:.3f}",
                        p_tp_entry=features.p_sl_entry, edge=features.edge_short,
                        vol_ratio=features.vol_ratio)
        else:
            return EntryDecision(enter=False, direction=None,
                        reason=f"no edge: long={features.edge_long:.3f} short={features.edge_short:.3f}",
                        p_tp_entry=features.p_tp_entry, edge=max(features.edge_long,features.edge_short),
                        vol_ratio=features.vol_ratio)