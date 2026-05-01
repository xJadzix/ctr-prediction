"""
Kafka producer that reads ad impressions from val_split.parquet
and sends them to ad-impressions topic.
"""

from kafka import KafkaProducer
import json
import time
import polars as pl
from pathlib import Path

def add_features(df):
    """Add time features and is_app flag (same logic as in training)."""
    return (
        df
        .with_columns(pl.col("hour").cast(pl.String).alias("hour_str"))
        .with_columns([
            pl.col("hour_str").str.slice(4, 2).cast(pl.Int8).alias("day"),
            pl.col("hour_str").str.slice(6, 2).cast(pl.Int8).alias("hour_of_day"),
        ])
        .with_columns(((pl.col("day") - 21 + 1) % 7).alias("day_of_week"))
        .with_columns(pl.col("day_of_week").is_in([5, 6]).alias("is_weekend"))
        .with_columns((pl.col("app_id") != "ecad2386").alias("is_app"))
        .drop(["hour_str", "id", "hour", "day", "device_id", "device_ip", "click"])
    )

# Path to val data
DATA_PATH = Path("../data/interim/val_split.parquet")

# How many messages to send and how fast
N_MESSAGES = 100 # only read 100 first rows
DELAY_SECONDS = 1.0

# Load data
print("Loading val data...")
df = add_features(pl.scan_parquet(DATA_PATH).head(N_MESSAGES)).collect()
print(f"Loaded {len(df)} rows.")

# Kafka topic name
TOPIC = "ad-impressions"

def serialize_message(message):
    """Convert dict to JSON bytes for Kafka."""
    json_string = json.dumps(message) # from python dictionary to JSON
    json_bytes = json_string.encode("utf-8") # from string to bytes
    return json_bytes

# Connect to Kafka running on localhost
print("Connecting to Kafka...")
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    # Converting message before sending
    value_serializer=serialize_message
)
print("Producer connected to Kafka.")

# Topic name
TOPIC = "ad-impressions"

# Convert each row to dict and send
records = df.to_dicts()
print(f"\nSending {N_MESSAGES} messages, one every {DELAY_SECONDS}s...\n")

# Send a few test messages
for i, record in enumerate(records): # pairs (index,value) for rows in records
    # Add unique impression ID
    record["impression_id"] = f"imp_{i}" # unique ID to identify impressions
    # Send to Kafka
    producer.send(TOPIC, value = record)
    print(f"Sent message {i+1}/{N_MESSAGES}: impression_id = {record['impression_id']}")
    time.sleep(DELAY_SECONDS)

# Make sure all messages are sent before closing
producer.flush()
producer.close() # close connection

print(f"\nProducer finished. Sent {N_MESSAGES} messages.")