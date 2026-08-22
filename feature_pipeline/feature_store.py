import os
import hopsworks
from dotenv import load_dotenv
import pandas as pd


load_dotenv()

def _get_hopsworks_api_key():
    key = os.getenv("HOPSWORKS_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets.get("HOPSWORKS_API_KEY")
    except Exception:
        return None

HOPSWORKS_API_KEY = _get_hopsworks_api_key()


def get_feature_store():
    """
    Log in to Hopsworks and return the feature store handle.
    """
    if not HOPSWORKS_API_KEY:
        raise ValueError("HOPSWORKS_API_KEY not found. Check your .env file.")

    project = hopsworks.login(api_key_value=HOPSWORKS_API_KEY)
    return project.get_feature_store()


def get_or_create_aqi_feature_group(fs):
    """
    Get the AQI feature group if it exists, or create it if this is the
    first time we're writing data.

    Args:
        fs: Hopsworks feature store handle (from get_feature_store()).

    Returns:
        FeatureGroup: the aqi_weather_features feature group.
    """
    feature_group = fs.get_or_create_feature_group(
        name="aqi_weather_features",
        version=1,
        description="Hourly weather and air pollution features for Rawalpindi",
        primary_key=["city", "timestamp"],
        event_time="timestamp",
        time_travel_format="HUDI",
    )
    return feature_group




def insert_row(feature_group, row: dict):
    """
    Insert a single feature row into the given feature group.
    Args:
        feature_group: The Hopsworks FeatureGroup to write to.
        row (dict): A single flat feature row (from fetch_current_features).
    """
    df = pd.DataFrame([row])
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Explicitly enforce float64 for weather columns — pandas can silently
    # infer int64 for a single-row DataFrame when a float value has no
    # fractional part (e.g. 41.0), which breaks Hopsworks' schema check.
    weather_columns = ["temperature", "humidity", "pressure", "wind_speed", "wind_deg"]
    for col in weather_columns:
        df[col] = df[col].astype("float64")

    feature_group.insert(df)


def get_latest_rows(feature_group, n: int = 5):
    """
    Read the most recent N rows from the feature group, sorted by timestamp
    descending (most recent first).

    Args:
        feature_group: The Hopsworks FeatureGroup to read from.
        n (int): Number of most recent rows to return.

    Returns:
        pd.DataFrame: The most recent rows.
    """
    df = feature_group.read()
    df = df.sort_values("timestamp", ascending=False)
    return df.head(n)