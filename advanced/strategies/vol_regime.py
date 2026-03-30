from .data_structures import EntryFeatures, EntryDecision
from .base import Strategy

class VolRegimeStrategy(Strategy):
    
    def __init__(self):
        pass

    def __call__(self, features: EntryFeatures,
                config: dict = {}) -> EntryDecision:
        VOL_RATIO_THRESHOLD = config.get("vol_ratio_threshold", 1.5)

        if features.vol_ratio < VOL_RATIO_THRESHOLD:
            return EntryDecision(
                enter=False, direction=None,
                reason=f"vol too low: {features.vol_ratio:.2f}",
                p_tp_entry=features.p_tp_entry,
                edge=0.0,
                vol_ratio=features.vol_ratio
            )

        # vol spike — mean reversion expected, fade the spike
        # sigma > sigma_bar means vol elevated above long-run mean
        # direction: if price moved up to cause the spike, go short (and vice versa)
        direction = "short" if features.sigma_now > features.sigma_bar else "long"

        return EntryDecision(
            enter=True, direction=direction,
            reason=f"vol spike={features.vol_ratio:.2f}",
            p_tp_entry=features.p_tp_entry,
            edge=0.0,
            vol_ratio=features.vol_ratio
        )