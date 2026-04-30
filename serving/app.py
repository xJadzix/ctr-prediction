"""
FastAPI application for serving CTR predictions.
Loads LightGBM model and isotonic calibrator at startup.
"""

import lightgbm as lgb
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import os


# Path to models directory (relative to this file) (try local path first, then container path)
local_models = Path(__file__).parent.parent / "models"
container_models = Path(__file__).parent / "models"

if local_models.exists():
    MODELS_DIR = local_models
else:
    MODELS_DIR = container_models
print(f"Using models from: {MODELS_DIR}")

MODEL_VERSION = "lightgbm_final"

# Load model, encoder and calibrator at startup
print("Loading model components...")
model = lgb.Booster(model_file=str(MODELS_DIR / "lightgbm_final.txt"))
ordinal_encoder = joblib.load(MODELS_DIR / "ordinal_encoder.pkl")
calibrator = joblib.load(MODELS_DIR / "isotonic_calibrator.pkl")
print("All components loaded.")

# List of categorical columns expected by the encoder
CATEGORICAL_COLS = [
    "C1", "banner_pos", "device_type", "device_conn_type",
    "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21",
    "hour_of_day", "day_of_week",
    "site_id", "site_domain", "site_category",
    "app_id", "app_domain", "app_category",
    "device_model",
]

# Input data schema using Pydantic (checking datatypes in the incoming JSON, generating API documentation)
class PredictionRequest(BaseModel):
    C1: int
    banner_pos: int
    device_type: int
    device_conn_type: int
    C14: int
    C15: int
    C16: int
    C17: int
    C18: int
    C19: int
    C20: int
    C21: int
    hour_of_day: int
    day_of_week: int
    site_id: str
    site_domain: str
    site_category: str
    app_id: str
    app_domain: str
    app_category: str
    device_model: str
    is_weekend: bool
    is_app: bool

# Output data schema
class PredictionResponse(BaseModel):
    raw_prediction: float
    calibrated_prediction: float
    model_version: str

# Create FastAPI app
app = FastAPI(
    title = "CTR Prediction API",
    description = "Predicts click-through rate using calibrated LightGBM model",
    version = "1.0.0"
)

# Defining endpoint
@app.get("/health")
def health_check():
    """Check if service is running."""
    return {"status": "healthy"}

@app.get("/info")
def model_info():
    """Return model metadata."""
    return {
        "model_type": "LightGBM with isotonic calibrator",
        "num_trees": model.num_trees(),
        "num_features": model.num_feature(),
        "version": MODEL_VERSION
    }

# POST - sending data 
@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """Generate calibrated CTR prediction for a single impression."""

    # Convert request to DataFrame (single row)
    input_dict = request.model_dump()
    df = pd.DataFrame([input_dict])

    # Apply ordinal encoding to categorical columns
    df[CATEGORICAL_COLS] = ordinal_encoder.transform(df[CATEGORICAL_COLS])

    # Convert boolean columns to int8
    df["is_weekend"] = df["is_weekend"].astype("int8")
    df["is_app"] = df["is_app"].astype("int8")

    # Get raw prediction from model
    raw_pred = model.predict(df.values)[0]

    # Apply calibration
    calibrated_pred = calibrator.transform([raw_pred])[0]

    return PredictionResponse(
        raw_prediction = float(raw_pred),
        calibrated_prediction = float(calibrated_pred),
        model_version = MODEL_VERSION
    )
