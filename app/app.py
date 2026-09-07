"""
FastAPI backend for the Exit Poll Prediction System.
Connects directly to src/predictor.py — no extra model/utils wrappers needed.
Outputs (CSV + JSON) are always written to the outputs/ folder.
"""

import os
import json
import sys

# ── Make sure the project root is on sys.path so `src` is importable ─────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.predictor import build_profiles, predict, TOTAL_SEATS, MAJORITY, CONFIDENCE, DATASET_FILES, resolve_new_poll_path
from src.ai_layer import generate_chatgpt_prompt, apply_sentiment

app = FastAPI(title="Exit Poll Prediction API", version="1.0.0")

# Allow local development calls from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Paths (relative to project root, i.e. cwd when running main.py) ──────────
TRAINING_FILE = os.path.join(ROOT, "data", "training_data.csv")
OUTPUTS_DIR   = os.path.join(ROOT, "outputs")

VALID_DATASETS = {
    key: os.path.join(ROOT, path)
    for key, path in DATASET_FILES.items()
}

# ── Pre-load bias profiles once at startup ────────────────────────────────────
profiles: dict = {}

@app.on_event("startup")
def startup_event():
    global profiles
    print("Building bias profiles from training data...")
    profiles = build_profiles(TRAINING_FILE)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    print(f"Model ready. {len(profiles)} role profiles loaded.")


# ── Request / Response schemas ────────────────────────────────────────────────
class PredictRequest(BaseModel):
    dataset: str   # e.g. "dataset_1"

class AllianceResult(BaseModel):
    alliance: str
    role: str
    n_agencies: int
    raw_median: float
    bias_correction: float
    point_estimate: int
    interval_lo: int
    interval_hi: int
    confidence: float

class SummaryResult(BaseModel):
    likely_winner: str
    point_estimate: int
    interval_lo: int
    interval_hi: int
    majority_likely: bool

class PredictResponse(BaseModel):
    election: str
    total_seats: int
    majority: int
    interval_pct: int
    dataset_used: str
    alliances: list[AllianceResult]
    summary: SummaryResult
    ai_prompt: str = ""

class AIPredictRequest(BaseModel):
    dataset: str
    sentiment_data: dict


# ── API Routes ────────────────────────────────────────────────────────────────

@app.get("/api/datasets")
def list_datasets():
    """Return the list of available dataset identifiers."""
    return {"datasets": list(VALID_DATASETS.keys())}


@app.post("/api/predict", response_model=PredictResponse)
def run_prediction(req: PredictRequest):
    """Run the statistical prediction model on the selected dataset."""
    if not profiles:
        raise HTTPException(status_code=503, detail="Model not ready — profiles not built yet.")

    dataset_key = req.dataset
    if dataset_key not in VALID_DATASETS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown dataset '{dataset_key}'. Valid options: {list(VALID_DATASETS.keys())}"
        )

    csv_path = resolve_new_poll_path(dataset_key)
    if not os.path.isfile(csv_path):
        csv_path = VALID_DATASETS[dataset_key]
    if not os.path.isfile(csv_path):
        raise HTTPException(status_code=404, detail=f"Dataset file not found: {csv_path}")

    # Run the statistical prediction for the dataset selected in Data Manager
    result_df = predict(dataset_key, profiles, conf=CONFIDENCE)

    # Save outputs to outputs/ folder
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    csv_out  = os.path.join(OUTPUTS_DIR, "prediction_output.csv")
    json_out = os.path.join(OUTPUTS_DIR, "prediction_output.json")
    result_df.to_csv(csv_out, index=False)

    # Build response payload
    alliances_list = []
    for _, row in result_df.iterrows():
        alliances_list.append(AllianceResult(
            alliance        = row["Alliance"],
            role            = row["Role"],
            n_agencies      = int(row["N_Agencies"]),
            raw_median      = float(row["Raw_Median"]),
            bias_correction = float(row["Bias_Correction"]),
            point_estimate  = int(row["Point_Estimate"]),
            interval_lo     = int(row["Interval_Lo"]),
            interval_hi     = int(row["Interval_Hi"]),
            confidence      = float(row["Confidence"]),
        ))

    winner = result_df.iloc[0]
    summary = SummaryResult(
        likely_winner   = str(winner["Alliance"]),
        point_estimate  = int(winner["Point_Estimate"]),
        interval_lo     = int(winner["Interval_Lo"]),
        interval_hi     = int(winner["Interval_Hi"]),
        majority_likely = bool(winner["Point_Estimate"] >= MAJORITY),
    )

    payload = PredictResponse(
        election     = "West Bengal Assembly 2026",
        total_seats  = TOTAL_SEATS,
        majority     = MAJORITY,
        interval_pct = int(CONFIDENCE * 100),
        dataset_used = dataset_key,
        alliances    = alliances_list,
        summary      = summary,
        ai_prompt    = generate_chatgpt_prompt([a.model_dump() for a in alliances_list])
    )

    # Persist JSON output
    with open(json_out, "w") as f:
        json.dump(payload.model_dump(), f, indent=2)

    return payload

@app.post("/api/apply_ai")
def run_ai_prediction(req: AIPredictRequest):
    """Run the AI sentiment prediction model on top of statistical baseline."""
    if not profiles:
        raise HTTPException(status_code=503, detail="Model not ready — profiles not built yet.")

    dataset_key = req.dataset
    if dataset_key not in VALID_DATASETS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown dataset '{dataset_key}'. Valid options: {list(VALID_DATASETS.keys())}"
        )

    csv_path = resolve_new_poll_path(dataset_key)
    if not os.path.isfile(csv_path):
        csv_path = VALID_DATASETS[dataset_key]
    if not os.path.isfile(csv_path):
        raise HTTPException(status_code=404, detail=f"Dataset file not found: {csv_path}")
    
    # Run statistical prediction for the dataset selected in Data Manager
    result_df = predict(dataset_key, profiles, conf=CONFIDENCE)
    
    # Build baseline alliances
    alliances_list = []
    for _, row in result_df.iterrows():
        alliances_list.append({
            "alliance":        row["Alliance"],
            "role":            row["Role"],
            "point_estimate":  int(row["Point_Estimate"]),
            "interval_lo":     int(row["Interval_Lo"]),
            "interval_hi":     int(row["Interval_Hi"]),
            "confidence":      float(row["Confidence"]),
        })

    baseline = {"alliances": alliances_list}
    
    # Apply sentiment
    results = apply_sentiment(baseline, req.sentiment_data)
    
    # Build summary
    winner = results[0]
    maj = winner["final_estimate"] >= MAJORITY
    stat_w = result_df.iloc[0]["Alliance"]
    
    return {
        "dataset_used": dataset_key,
        "results": results,
        "summary": {
            "stat_winner": stat_w,
            "ai_winner": winner["alliance"],
            "majority_likely": maj
        }
    }


# ── Serve the frontend ────────────────────────────────────────────────────────
# Mount the app/ directory at /static so JS/CSS/sub-pages are accessible.
app.mount("/static", StaticFiles(directory=os.path.join(ROOT, "app")), name="static")

@app.get("/")
def serve_index():
    """Serve the main dashboard HTML."""
    return FileResponse(os.path.join(ROOT, "app", "index.html"))

@app.get("/overview")
def serve_overview():
    """Serve the overview sub-page."""
    return FileResponse(os.path.join(ROOT, "app", "overview.html"))
