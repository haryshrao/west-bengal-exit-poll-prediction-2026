"""
West Bengal Exit Poll Prediction System
----------------------------------------
Files expected in the same directory:
  training_data.csv  - historical exit poll data (2011, 2016, 2021)
  2026.csv           - new exit poll data (same format, Actual Seats = 0)

Run this FIRST, then run wb_ai_layer.py
Output: prediction_output.csv  +  prediction_output.json
"""

import json
import os
import numpy as np
import pandas as pd
from scipy import stats

# ── CONFIG ────────────────────────────────────────────────────────────────────

import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TRAINING_FILE = os.path.join(PROJECT_ROOT, "data", "training_data.csv")
DATASET_FILES = {
    "2026":      os.path.join(PROJECT_ROOT, "data", "2026.csv"),
    "dataset_1": os.path.join(PROJECT_ROOT, "data", "dataset_1.csv"),
    "dataset_2": os.path.join(PROJECT_ROOT, "data", "dataset_2.csv"),
    "dataset_3": os.path.join(PROJECT_ROOT, "data", "dataset_3.csv"),
}

DEFAULT_DATASET = "dataset_1"
if len(sys.argv) > 1:
    NEW_POLL_FILE = sys.argv[1]
else:
    NEW_POLL_FILE = DEFAULT_DATASET

TOTAL_SEATS   = 294
MAJORITY      = 148
CONFIDENCE    = 0.80

# Map each alliance name to a canonical role.
# Edit the 2026 block to match your actual 2026.csv alliance names.
ALLIANCE_ROLE_MAP = {
    # 2011
    "TMC+INC":    "DOMINANT",
    "LEFT FRONT": "MAIN_OPP",
    # 2016
    "TMC":        "DOMINANT",
    "CPIM+INC":   "MAIN_OPP",
    # 2021
    "TMC/TMC+":   "DOMINANT",
    "CONG+LEFT+": "MAIN_OPP",
    "BJP/BJP+":   "BJP_FAMILY",
    # dataset_1 / dataset_2 / dataset_3 alliance names
    "BJP+":       "BJP_FAMILY",
    "TMC+":       "DOMINANT",
    "OTHERS+":    "OTHERS",
}

FALLBACK_PROFILES = {
    "DOMINANT":   {"mean_error": -44.1, "mae": 46.0, "agency_std": 27.3, "avg_spread": 103.7, "n": 3},
    "MAIN_OPP":   {"mean_error": +18.6, "mae": 22.9, "agency_std": 20.8, "avg_spread":  67.0, "n": 3},
    "BJP_FAMILY": {"mean_error": +26.7, "mae": 27.4, "agency_std": 21.4, "avg_spread":  73.0, "n": 3},
    "OTHERS":     {"mean_error":  +0.3, "mae":  6.0, "agency_std":  5.7, "avg_spread":  18.0, "n": 2},
}


def resolve_new_poll_path(dataset_or_path):
    """Resolve a UI dataset key like 'dataset_2' or a direct CSV path."""
    if dataset_or_path in DATASET_FILES:
        return DATASET_FILES[dataset_or_path]

    if os.path.isfile(dataset_or_path):
        return dataset_or_path

    valid = ", ".join(DATASET_FILES.keys())
    raise ValueError(
        f"Unknown dataset or file '{dataset_or_path}'. "
        f"Use one of: {valid}, or pass a valid CSV path."
    )


# ── BUILD PROFILES FROM TRAINING DATA ─────────────────────────────────────────

def build_profiles(training_path):
    df = pd.read_csv(training_path)
    df = df[~df["Agency"].str.contains("Average|average", na=False)]
    df = df.dropna(subset=["Predicted Seats"])
    df["Role"] = df["Alliance"].map(ALLIANCE_ROLE_MAP).fillna("OTHERS")

    role_records = {r: [] for r in ["DOMINANT", "MAIN_OPP", "BJP_FAMILY", "OTHERS"]}

    for (year, role), grp in df.groupby(["Year", "Role"]):
        preds  = grp["Predicted Seats"].values.astype(float)
        actual = grp["Actual Seats"].iloc[0]
        if len(preds) == 0:
            continue
        errors = preds - actual
        role_records[role].append({
            "mean_error": float(np.mean(errors)),
            "mae":        float(np.mean(np.abs(errors))),
            "agency_std": float(np.std(preds, ddof=1)) if len(preds) > 1 else 0.0,
            "spread":     float(preds.max() - preds.min()),
        })

    profiles = {}
    for role, records in role_records.items():
        if not records:
            profiles[role] = FALLBACK_PROFILES[role]
            continue
        profiles[role] = {
            "mean_error": float(np.mean([r["mean_error"] for r in records])),
            "mae":        float(np.mean([r["mae"]        for r in records])),
            "agency_std": float(np.mean([r["agency_std"] for r in records])),
            "avg_spread": float(np.mean([r["spread"]     for r in records])),
            "n":          len(records),
        }
    return profiles


# ── CORE STATS ────────────────────────────────────────────────────────────────

def poll_stats(preds):
    arr = np.array([p for p in preds if p is not None and not np.isnan(p)], dtype=float)
    n = len(arr)
    if n == 0:
        raise ValueError("No valid predictions.")
    return {
        "n":      n,
        "mean":   float(np.mean(arr)),
        "median": float(np.median(arr)),
        "std":    float(np.std(arr, ddof=1)) if n > 1 else 0.0,
        "spread": float(arr.max() - arr.min()),
        "min":    float(arr.min()),
        "max":    float(arr.max()),
    }


def bias_correct(raw_median, profile):
    return float(np.clip(raw_median - profile["mean_error"], 0, TOTAL_SEATS))


def prediction_interval(corrected, ps, profile, conf=0.80):
    sigma_agency = max(ps["std"], profile["agency_std"] * 0.5)
    sigma_hist   = profile["mae"] * np.sqrt(np.pi / 2)
    sigma_total  = np.sqrt(sigma_agency**2 + sigma_hist**2)
    df     = max(profile["n"] - 1, 1)
    t_crit = stats.t.ppf((1 + conf) / 2, df=df)
    margin = t_crit * sigma_total
    lo = float(np.clip(corrected - margin, 0, TOTAL_SEATS))
    hi = float(np.clip(corrected + margin, 0, TOTAL_SEATS))
    return lo, hi


def spread_confidence(ps, profile):
    if profile["avg_spread"] == 0 or ps["n"] < 2:
        return 0.60
    ratio = ps["spread"] / profile["avg_spread"]
    raw   = 1 / (1 + np.exp(3 * (ratio - 0.8)))
    return float(round(0.20 + 0.75 * raw, 3))


# ── PREDICTION ────────────────────────────────────────────────────────────────

def predict(new_poll_path, profiles, conf=CONFIDENCE):
    new_poll_path = resolve_new_poll_path(new_poll_path)
    df = pd.read_csv(new_poll_path)
    df = df.dropna(subset=["Predicted Seats"])
    df["Role"] = df["Alliance"].map(ALLIANCE_ROLE_MAP).fillna("OTHERS")

    rows = []
    for alliance, grp in df.groupby("Alliance"):
        role    = grp["Role"].iloc[0]
        preds   = grp["Predicted Seats"].tolist()
        profile = profiles.get(role, profiles["OTHERS"])

        ps         = poll_stats(preds)
        corrected  = bias_correct(ps["median"], profile)
        lo, hi     = prediction_interval(corrected, ps, profile, conf)
        confidence = spread_confidence(ps, profile)

        rows.append({
            "Alliance":        alliance,
            "Role":            role,
            "N_Agencies":      ps["n"],
            "Raw_Mean":        round(ps["mean"], 1),
            "Raw_Median":      round(ps["median"], 1),
            "Agency_Std":      round(ps["std"], 1),
            "Spread":          round(ps["spread"], 1),
            "Bias_Correction": round(-profile["mean_error"], 1),
            "Point_Estimate":  round(corrected),
            "Interval_Lo":     round(lo),
            "Interval_Hi":     round(hi),
            "Confidence":      confidence,
        })

    result = pd.DataFrame(rows)

    total = result["Point_Estimate"].sum()
    if total > 0 and abs(total - TOTAL_SEATS) > 5:
        scale = TOTAL_SEATS / total
        result["Point_Estimate"] = (result["Point_Estimate"] * scale).round().astype(int)
        result["Interval_Lo"]    = (result["Interval_Lo"]    * scale).round().astype(int)
        result["Interval_Hi"]    = (result["Interval_Hi"]    * scale).round().astype(int)

    result = result.sort_values("Point_Estimate", ascending=False).reset_index(drop=True)
    return result


# ── PRINT REPORT ──────────────────────────────────────────────────────────────

def print_report(result):
    sep = "-" * 70
    print(f"\n{'='*70}")
    print(f"  WEST BENGAL 2026 - STATISTICAL PREDICTION (no AI layer)")
    print(f"  Interval coverage: {int(CONFIDENCE*100)}%  |  Total seats: {TOTAL_SEATS}  |  Majority: {MAJORITY}")
    print(f"{'='*70}\n")

    for _, row in result.iterrows():
        conf_label = (
            "HIGH"      if row["Confidence"] >= 0.75 else
            "MODERATE"  if row["Confidence"] >= 0.55 else
            "LOW"       if row["Confidence"] >= 0.35 else "VERY LOW"
        )
        print(f"  {row['Alliance']}  [{row['Role']}]")
        print(f"  {sep}")
        print(f"  Agencies          : {row['N_Agencies']}")
        print(f"  Raw median        : {row['Raw_Median']}  (spread={row['Spread']}, std={row['Agency_Std']})")
        print(f"  Bias correction   : {row['Bias_Correction']:+.0f} seats")
        print(f"  Point estimate    : {row['Point_Estimate']} seats")
        print(f"  Prediction range  : {row['Interval_Lo']} - {row['Interval_Hi']} seats")
        print(f"  Agency confidence : {conf_label}  ({row['Confidence']:.0%})\n")

    winner = result.iloc[0]
    maj    = winner["Point_Estimate"] >= MAJORITY
    print(f"{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"  Likely winner   : {winner['Alliance']}")
    print(f"  Point estimate  : {winner['Point_Estimate']} seats")
    print(f"  Range           : {winner['Interval_Lo']} - {winner['Interval_Hi']}")
    print(f"  Majority likely : {'YES' if maj else 'NO - hung assembly possible'}")
    print(f"{'='*70}\n")
    print("  Run wb_ai_layer.py next to add ChatGPT sentiment adjustment (no API key needed).")


# ── SAVE JSON FOR AI LAYER ────────────────────────────────────────────────────

def save_json(result, path="prediction_output.json"):
    alliances_list = []
    for _, row in result.iterrows():
        alliances_list.append({
            "alliance":        row["Alliance"],
            "role":            row["Role"],
            "n_agencies":      int(row["N_Agencies"]),
            "raw_median":      float(row["Raw_Median"]),
            "bias_correction": float(row["Bias_Correction"]),
            "point_estimate":  int(row["Point_Estimate"]),
            "interval_lo":     int(row["Interval_Lo"]),
            "interval_hi":     int(row["Interval_Hi"]),
            "confidence":      float(row["Confidence"]),
        })

    winner = result.iloc[0]
    payload = {
        "election":     "West Bengal Assembly 2026",
        "total_seats":  TOTAL_SEATS,
        "majority":     MAJORITY,
        "interval_pct": int(CONFIDENCE * 100),
        "alliances":    alliances_list,
        "summary": {
            "likely_winner":   winner["Alliance"],
            "point_estimate":  int(winner["Point_Estimate"]),
            "interval_lo":     int(winner["Interval_Lo"]),
            "interval_hi":     int(winner["Interval_Hi"]),
            "majority_likely": bool(winner["Point_Estimate"] >= MAJORITY),
        },
    }

    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  JSON saved to {path}")


# ── RUN ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Building profiles from training data...")
    profiles = build_profiles(TRAINING_FILE)

    print("Profile summary (mean error per role):")
    for role, p in profiles.items():
        direction = "UNDER" if p["mean_error"] < 0 else "OVER"
        print(f"  {role:<12}  mean_error={p['mean_error']:+.1f}  mae={p['mae']:.1f}  ({direction})")

    print(f"\nRunning prediction on {NEW_POLL_FILE}...")
    result = predict(NEW_POLL_FILE, profiles)

    print_report(result)

    import os
    os.makedirs("outputs", exist_ok=True)
    result.to_csv("outputs/prediction_output.csv", index=False)
    print("  CSV saved to outputs/prediction_output.csv")

    save_json(result, "outputs/prediction_output.json")
