"""
Kafka consumer that reads ad impressions and generates calibrated CTR predictions
using LightGBM model with isotonic calibration."""

from kafka import KafkaConsumer
import json
import lightgbm as lgb
import joblib
import pandas as pd
from pathlib import Path

# Path to models directory
MODELS_DIR = Path("../models")

# Categorical columns expected by ordinal encoder
CATEGORICAL_COLS = [
    "C1", "banner_pos", "device_type", "device_conn_type",
    "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21",
    "hour_of_day", "day_of_week",
    "site_id", "site_domain", "site_category",
    "app_id", "app_domain", "app_category",
    "device_model",
]

# Load model, encoder and calibrator
print("Loading model components...")
model = lgb.Booster(model_file=str(MODELS_DIR / "lightgbm_final.txt"))
ordinal_encoder = joblib.load(MODELS_DIR / "ordinal_encoder.pkl")
calibrator = joblib.load(MODELS_DIR / "isotonic_calibrator.pkl")
print("Model, encoder, and calibrator loaded.\n")


def deserialize_message(message_bytes):
    """Convert Kafka bytes back to Python dict."""
    json_string = message_bytes.decode("utf-8") # bytes to string
    message_dict = json.loads(json_string) # JSON to dictionary
    return message_dict

# Connect to Kafka and subscribe to topic
print("Connecting to Kafka...")
consumer = KafkaConsumer(
    "ad-impressions", # topic name
    bootstrap_servers="localhost:9092",
    value_deserializer=deserialize_message,
    auto_offset_reset="latest",
    group_id="ctr-prediction-consumer", # consumer group id
)
print("Consumer connected to Kafka. Waiting for messages...")

# Process messages
for message in consumer:
    # Get the impression data
    impression = message.value
    impression_id = impression.pop("impression_id") # delete the id from dictionary and return its value
    # Convert to DataFrame (one row)
    df = pd.DataFrame([impression])
    # Apply ordinal encoding to categorical columns
    df[CATEGORICAL_COLS] = ordinal_encoder.transform(df[CATEGORICAL_COLS])
    # Convert boolean columns to int8
    df["is_weekend"] = df["is_weekend"].astype("int8")
    df["is_app"] = df["is_app"].astype("int8")
    # Get raw prediction from model
    raw_prediction = model.predict(df.values)[0]
    # Apply isotonic calibration
    calibrated_prediction = calibrator.transform([raw_prediction])[0]
    # Print results
    print(f"{impression_id}: raw = {raw_prediction:.4f}, calibrated = {calibrated_prediction:.4f}")