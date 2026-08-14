import os
import hopsworks
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

HOPSWORKS_API_KEY = os.getenv("HOPSWORKS_API_KEY")


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