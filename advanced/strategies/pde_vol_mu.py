from .data_structures import EntryFeatures, EntryDecision
from .base import Strategy

class PdeVolMuStrategy(Strategy):
    
    def __init__(self):
        pass

    def __call__(self, features: EntryFeatures,
                 config: dict={}) -> EntryDecision:
    # --- MU DIRECTION STRATEGY (uncomment to use) ---------------------
    
        MU_THRESHOLD_LONG   = config.get("mu_threshold_long", 0.05)
        MU_THRESHOLD_SHORT  = config.get("mu_threshold_short", -0.05)
        EDGE_THRESHOLD = config.get("edge_threshold", 0.03)
        VOL_MAX        = config.get("vol_max", 1.5)
        VOL_STRONG     = config.get("vol_strong", 1.0)
        P_THRESHOLD    = config.get("p_threshold", 0.46)

        # 1️⃣ Volatility regime filter
        if (features.vol_ratio > VOL_MAX):
            return EntryDecision(
                enter=False,
                direction=None,
                reason=f"vol too high: {features.vol_ratio:.2f}",
                p_tp_entry=features.p_tp_entry,
                edge=0.0,
                vol_ratio=features.vol_ratio
            )

        # 2️⃣ Directional bias from drift
        long_bias  = features.mu_now > MU_THRESHOLD_LONG
        short_bias = features.mu_now < MU_THRESHOLD_SHORT

        # 3️⃣ Strong regime (best performance)
        if (features.vol_ratio < VOL_STRONG):

            if (long_bias and features.edge_long > EDGE_THRESHOLD and features.p_tp_entry > P_THRESHOLD):
                return EntryDecision(
                    enter=True,
                    direction="long",
                    reason=f"strong regime long μ={features.mu_now:.3f}",
                    p_tp_entry=features.p_tp_entry,
                    edge=features.edge_long,
                    vol_ratio=features.vol_ratio
                )

            if (short_bias and features.edge_short > EDGE_THRESHOLD and features.p_sl_entry > P_THRESHOLD):
                return EntryDecision(
                    enter=True,
                    direction="short",
                    reason=f"strong regime short μ={features.mu_now:.3f}",
                    p_tp_entry=features.p_sl_entry,
                    edge=features.edge_short,
                    vol_ratio=features.vol_ratio
                )

        # 4️⃣ Moderate regime (require stronger edge)
        if (features.edge_long > EDGE_THRESHOLD * 1.5 and features.p_tp_entry > P_THRESHOLD + 0.02):
            if features.mu_now > 0:
                return EntryDecision(
                    enter=True,
                    direction="long",
                    reason=f"moderate regime long μ={features.mu_now:.3f}",
                    p_tp_entry=features.p_tp_entry,
                    edge=features.edge_long,
                    vol_ratio=features.vol_ratio
                )

        if (features.edge_short > EDGE_THRESHOLD * 1.5 and features.p_sl_entry > P_THRESHOLD + 0.02):
            if (features.mu_now < 0):
                return EntryDecision(
                    enter=True,
                    direction="short",
                    reason=f"moderate regime short μ={features.mu_now:.3f}",
                    p_tp_entry=features.p_sl_entry,
                    edge=features.edge_short,
                    vol_ratio=features.vol_ratio
                )

        # 5️⃣ No signal
        return EntryDecision(
            enter=False,
            direction=None,
            reason=f"no signal μ={features.mu_now:.3f}",
            p_tp_entry=features.p_tp_entry,
            edge=0.0,
            vol_ratio=features.vol_ratio
        )