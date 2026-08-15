import os
import time
from datetime import datetime, timezone, timedelta

import requests
import pandas as pd
from dotenv import load_dotenv

from feature_pipeline.config import CITY_NAME, LATITUDE, LONGITUDE
from feature_pipeline.feature_engineering import add_time_features
from feature_pipeline.feature_store import get_feature_store, get_or_create_aqi_feature_group

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
POLLUTION_HISTORY_URL = "http://api.openweathermap.org/data/2.5/air_pollution/history"


def fetch_historical_pollution(start_dt: datetime, end_dt: datetime) -> list[dict]:
    """
    Fetch historical air pollution data for the configured city between
    start_dt and end_dt (inclusive), and return a list of flat feature rows.

    Weather fields are set to None (not available for backfill under our
    free-tier approach). Each row is flagged with is_backfilled=True.

    Args:
        start_dt (datetime): Start of the range (UTC).
        end_dt (datetime): End of the range (UTC).

    Returns:
        list[dict]: One dict per hourly reading.
    """
    if not API_KEY:
        raise ValueError("OPENWEATHER_API_KEY not found. Check your .env file.")

    params = {
        "lat": LATITUDE,
        "lon": LONGITUDE,
        "start": int(start_dt.timestamp()),
        "end": int(end_dt.timestamp()),
        "appid": API_KEY,
    }

    response = requests.get(POLLUTION_HISTORY_URL, params=params)
    if response.status_code != 200:
        raise RuntimeError(
            f"Pollution history API failed: {response.status_code} - {response.text}"
        )

    entries = response.json()["list"]

    rows = []
    for entry in entries:
        row = {
            "city": CITY_NAME,
            "timestamp": datetime.fromtimestamp(entry["dt"], tz=timezone.utc),

            # Weather fields not available for backfill under our free-tier approach
            "temperature": None,
            "humidity": None,
            "pressure": None,
            "wind_speed": None,
            "wind_deg": None,

            "aqi": entry["main"]["aqi"],
            "co": entry["components"]["co"],
            "no2": entry["components"]["no2"],
            "so2": entry["components"]["so2"],
            "o3": entry["components"]["o3"],
            "pm2_5": entry["components"]["pm2_5"],
            "pm10": entry["components"]["pm10"],
            "nh3": entry["components"]["nh3"],

            "is_backfilled": True,
        }
        row = add_time_features(row)
        rows.append(row)

    return rows


def run_backfill(days_back: int = 30):
    """
    Backfill historical pollution data for the last `days_back` days and
    write it to the feature store.
    """
    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=days_back)

    print(f"Fetching historical pollution data from {start_dt} to {end_dt}...")
    rows = fetch_historical_pollution(start_dt, end_dt)
    print(f"Fetched {len(rows)} historical rows.")

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Explicitly type the all-null weather columns as float64,
    # since pandas can't infer a type from columns that are 100% None
    weather_columns = ["temperature", "humidity", "pressure", "wind_speed", "wind_deg"]
    for col in weather_columns:
        df[col] = df[col].astype("float64")

    print("Connecting to feature store...")
    fs = get_feature_store()
    fg = get_or_create_aqi_feature_group(fs)

    print("Inserting backfilled rows...")
    fg.insert(df)

    print("Backfill complete.")

if __name__ == "__main__":
    run_backfill(days_back=30)  