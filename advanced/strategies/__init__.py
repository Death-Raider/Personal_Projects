from .pde_vol_mu  import PdeVolMuStrategy
from .pde_edge  import PDEEdgeStrategy
from .vol_regime import VolRegimeStrategy
from .base import Strategy
from .always_buy import AlwaysBuyStrategy
from .data_structures import EntryFeatures, EntryDecision

STRATEGY_REGISTRY: dict[str, Strategy] = {
    "pde_vol_mu"   : PdeVolMuStrategy,
    "pde_edge"   : PDEEdgeStrategy,
    "vol_regime" : VolRegimeStrategy,
    'always_buy' : AlwaysBuyStrategy,
}