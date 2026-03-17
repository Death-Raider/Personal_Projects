"""
validate_incremental.py
========================
Validates that update_last_row produces identical results to
build_risk_features run on the full dataset.

Test protocol
-------------
1. Generate synthetic OHLCV data of length N_FULL
2. Split at N_BASE  (first half = "history", second half = "new bars")
3. Full computation:
       df_full = build_risk_features(all N_FULL rows)
4. Incremental computation:
       df_inc  = build_risk_features(first N_BASE rows)   # baseline
       for each new row in rows N_BASE → N_FULL:
           df_inc = update_last_row(df_inc, new_row)
5. Compare df_full.iloc[N_BASE:] vs df_inc.iloc[N_BASE:]
   row by row, column by column.
6. Report:
   - columns that match exactly (within floating-point tolerance)
   - columns with small but acceptable drift (carry-forward tier 3)
   - columns that diverge significantly (bugs)
"""

import numpy as np
import pandas as pd
import sys, os

# ── allow import from parent / same directory ────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Support both package layout (statistical_modeling.Risk_Modeling)
# and flat layout (Risk_Modeling directly in same folder)
try:
    from statistical_modeling.Risk_Modeling import build_risk_features, update_last_row
except ImportError:
    from Risk_Modeling import build_risk_features, update_last_row

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════

N_BASE   = 350    # rows used for initial full build
N_NEW    = 50     # new rows added incrementally  (total = N_BASE + N_NEW)
TF       = "M5"
SEED     = 42

# Tolerance for "match" — relative error < REL_TOL or absolute < ABS_TOL
REL_TOL  = 1e-4   # 0.01%
ABS_TOL  = 1e-6

# Carry-forward columns are expected to differ slightly — reported separately
CARRY_SUFFIXES = [
    "hptrend", "hpcycle", "hpcycle_z",
    "kmeans_regime", "kmeans_dist",
    "gmm_regime", "gmm_entropy",
    "dbscan_anomaly",
    "drawdown", "dd_duration",
    "cumulative_pnl",
]

# ══════════════════════════════════════════════════════════════════════════════
# SYNTHETIC DATA
# ══════════════════════════════════════════════════════════════════════════════

def make_ohlcv(n: int, seed: int = 42) -> pd.DataFrame:
    rng   = np.random.default_rng(seed)
    # Simulate a realistic gold-like price series
    close = 5000 + np.cumsum(rng.normal(0, 3.5, n))
    noise = np.abs(rng.normal(0, 1.5, n))
    high  = close + noise * rng.uniform(0.5, 2.0, n)
    low   = close - noise * rng.uniform(0.5, 2.0, n)
    open_ = close + rng.normal(0, 1.0, n)
    vol   = np.abs(rng.normal(1000, 300, n)) + 200

    dates = pd.date_range("2026-01-01", periods=n, freq="5min")
    return pd.DataFrame({
        "open"  : open_,
        "high"  : high,
        "low"   : low,
        "close" : close,
        "volume": vol,
    }, index=dates)

# ══════════════════════════════════════════════════════════════════════════════
# COMPARISON HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def is_close(a, b):
    """True if a and b are within tolerance."""
    if pd.isna(a) and pd.isna(b):
        return True
    if pd.isna(a) or pd.isna(b):
        return False
    abs_diff = abs(float(a) - float(b))
    if abs_diff < ABS_TOL:
        return True
    denom = max(abs(float(b)), 1e-12)
    return (abs_diff / denom) < REL_TOL


def classify_col(col: str, tag: str) -> str:
    """Return tier label for a column."""
    suffix = col[len(tag)+1:]  # strip "M5_" prefix
    for s in CARRY_SUFFIXES:
        if suffix.startswith(s):
            return "carry"
    if "gmm_prob" in col:
        return "carry"
    return "rolling"


def compare_rows(row_full: pd.Series, row_inc: pd.Series,
                 tag: str) -> dict:
    """
    Compare one row between full and incremental.
    Returns dict of {col: (full_val, inc_val, match, tier)}.
    """
    results = {}
    for col in row_full.index:
        if col not in row_inc.index:
            continue
        tier  = classify_col(col, tag)
        match = is_close(row_full[col], row_inc[col])
        results[col] = dict(
            full  = row_full[col],
            inc   = row_inc[col],
            match = match,
            tier  = tier,
        )
    return results

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    N_FULL = N_BASE + N_NEW
    tag    = TF.upper()

    print("=" * 65)
    print("  INCREMENTAL UPDATE VALIDATION")
    print("=" * 65)
    print(f"  N_BASE  : {N_BASE}  (initial full build)")
    print(f"  N_NEW   : {N_NEW}   (incremental bars)")
    print(f"  N_FULL  : {N_FULL}")
    print(f"  TF      : {TF}")
    print(f"  REL_TOL : {REL_TOL*100:.3f}%")
    print()

    # ── Step 1: generate data ──────────────────────────────────────────
    print("[1/4] Generating synthetic OHLCV ...")
    df_all  = make_ohlcv(N_FULL, SEED)
    df_base = df_all.iloc[:N_BASE].copy()
    df_new  = df_all.iloc[N_BASE:].copy()
    print(f"      Base: {len(df_base)} rows  |  New: {len(df_new)} rows")

    # ── Step 2: full computation on all N_FULL rows ────────────────────
    print("\n[2/4] Full computation on all rows ...")
    df_full = build_risk_features(df_all.copy(), TF)
    print(f"      Feature columns: {df_full.shape[1]}")

    # ── Step 3: incremental computation ───────────────────────────────
    print("\n[3/4] Incremental computation ...")
    print(f"      Building base on {N_BASE} rows ...")
    df_inc = build_risk_features(df_base.copy(), TF)
    print(f"      Appending {N_NEW} rows one at a time ...")

    mismatches_per_row = []

    for i in range(N_NEW):
        new_row = df_new.iloc[i].to_dict()
        df_inc  = update_last_row(df_inc, new_row, TF)

        # Compare this row against full computation
        row_idx  = N_BASE + i
        row_full = df_full.iloc[row_idx]
        row_inc  = df_inc.iloc[-1]
        results  = compare_rows(row_full, row_inc, tag)

        n_mismatch = sum(1 for v in results.values()
                          if not v["match"] and v["tier"] == "rolling")
        mismatches_per_row.append(n_mismatch)

        status = "OK" if n_mismatch == 0 else f"DIFF({n_mismatch})"
        print(f"      Row {row_idx:>4}  {status}")

    # ── Step 4: detailed column-level report ──────────────────────────
    print("\n[4/4] Detailed column comparison (last row) ...")

    row_full_last = df_full.iloc[-1]
    row_inc_last  = df_inc.iloc[-1]
    results_last  = compare_rows(row_full_last, row_inc_last, tag)

    # Sort by tier then match status
    rolling_ok   = []
    rolling_diff = []
    carry_ok     = []
    carry_diff   = []

    for col, info in sorted(results_last.items()):
        if info["tier"] == "carry":
            (carry_ok if info["match"] else carry_diff).append((col, info))
        else:
            (rolling_ok if info["match"] else rolling_diff).append((col, info))

    # ── Summary ────────────────────────────────────────────────────────
    n_roll_total = len(rolling_ok)  + len(rolling_diff)
    n_carr_total = len(carry_ok)    + len(carry_diff)
    n_total      = n_roll_total     + n_carr_total

    print()
    print("  SUMMARY")
    print(f"  {'─'*55}")
    print(f"  Total columns compared    : {n_total}")
    print(f"  Rolling tier — match      : {len(rolling_ok)}/{n_roll_total}  "
          f"{'✔' if len(rolling_diff)==0 else '✗'}")
    print(f"  Rolling tier — MISMATCH   : {len(rolling_diff)}/{n_roll_total}")
    print(f"  Carry-forward — match     : {len(carry_ok)}/{n_carr_total}")
    print(f"  Carry-forward — diff      : {len(carry_diff)}/{n_carr_total}  "
          f"(expected for tier-3)")
    print(f"  Max mismatch row          : "
          f"{max(mismatches_per_row) if mismatches_per_row else 0}")
    print(f"  Rows with any mismatch    : "
          f"{sum(1 for x in mismatches_per_row if x > 0)}/{N_NEW}")

    # ── Rolling mismatches (these are bugs) ────────────────────────────
    if rolling_diff:
        print()
        print(f"  ROLLING MISMATCHES  (these are bugs)")
        print(f"  {'─'*55}")
        print(f"  {'Column':<40} {'Full':>12} {'Incr':>12} {'RelErr':>8}")
        print(f"  {'─'*75}")
        for col, info in rolling_diff[:50]:   # cap at 50
            fv  = info["full"]
            iv  = info["inc"]
            rel = (abs(float(fv)-float(iv)) / (abs(float(fv))+1e-12)
                   if not (pd.isna(fv) or pd.isna(iv)) else float("nan"))
            print(f"  {col:<40} {str(fv)[:12]:>12} {str(iv)[:12]:>12} "
                  f"{rel*100:>7.3f}%")
        if len(rolling_diff) > 50:
            print(f"  ... and {len(rolling_diff)-50} more")
    else:
        print()
        print("  ✔  No rolling-tier mismatches — incremental is correct.")

    # ── Carry-forward diffs (expected, not bugs) ───────────────────────
    if carry_diff:
        print()
        print(f"  CARRY-FORWARD DIFFS  (expected — tier 3 columns)")
        print(f"  {'─'*55}")
        print(f"  {'Column':<40} {'Full':>12} {'Incr':>12}")
        print(f"  {'─'*66}")
        for col, info in carry_diff[:20]:
            print(f"  {col:<40} {str(info['full'])[:12]:>12} "
                  f"{str(info['inc'])[:12]:>12}")
        if len(carry_diff) > 20:
            print(f"  ... and {len(carry_diff)-20} more")

    # ── Per-row mismatch timeline ──────────────────────────────────────
    if any(x > 0 for x in mismatches_per_row):
        print()
        print("  PER-ROW ROLLING MISMATCH COUNT")
        print(f"  {'─'*40}")
        for i, m in enumerate(mismatches_per_row):
            if m > 0:
                print(f"  Row {N_BASE+i:>4}  : {m} mismatches")

    print()
    print("=" * 65)

    # Return pass/fail for CI use
    return len(rolling_diff) == 0


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)