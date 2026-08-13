import os
import hopsworks
from dotenv import load_dotenv

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
    )
    return feature_group