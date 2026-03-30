from dataclasses import dataclass
from typing import Optional

@dataclass
class EntryFeatures:
    mu_now:      float   # drift estimate from MuModel
    sigma_now:   float   # current vol (rolling w_sigma std)
    sigma_bar:   float   # long-run vol (rolling w_bar std)
    vol_ratio:   float   # sigma_now / sigma_bar
    pe:          float   # Peclet number |mu|*L / (0.5*sigma²)
    p_tp_entry:  float   # PDE surface value at x=0, sigma_now
    p_sl_entry:  float   # 1 - p_tp_entry
    edge_long:   float   # p_tp_entry - p_null
    edge_short:  float   # p_sl_entry - p_null
    surface_mu:  float   # mu used when current surface was built
    p_null:      float   # |SL| / (TP + |SL|)

@dataclass
class EntryDecision:
    enter:      bool
    direction:  Optional[str]   # "long" | "short" | None
    reason:     str
    p_tp_entry: float
    edge:       float
    vol_ratio:  float