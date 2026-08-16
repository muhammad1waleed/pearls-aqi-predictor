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


def run_backfill(days_back: int = 365, chunk_days: int = 30):
    """
    Backfill historical pollution data for the last `days_back` days,
    fetched in `chunk_days`-sized windows to avoid overly large single
    API calls, and write it to the feature store.
    """
    end_dt = datetime.now(timezone.utc)
    overall_start_dt = end_dt - timedelta(days=days_back)

    all_rows = []
    chunk_start = overall_start_dt

    while chunk_start < end_dt:
        chunk_end = min(chunk_start + timedelta(days=chunk_days), end_dt)

        print(f"Fetching {chunk_start.date()} to {chunk_end.date()}...")
        rows = fetch_historical_pollution(chunk_start, chunk_end)
        print(f"  -> {len(rows)} rows")
        all_rows.extend(rows)

        chunk_start = chunk_end
        time.sleep(1)  # be polite to the API, avoid rate-limit issues

    print(f"Total fetched: {len(all_rows)} rows")

    df = pd.DataFrame(all_rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    weather_columns = ["temperature", "humidity", "pressure", "wind_speed", "wind_deg"]
    for col in weather_columns:
        df[col] = df[col].astype("float64")

    # Drop exact duplicate timestamps that can occur at chunk boundaries
    df = df.drop_duplicates(subset=["city", "timestamp"]).reset_index(drop=True)

    print("Connecting to feature store...")
    fs = get_feature_store()
    fg = get_or_create_aqi_feature_group(fs)

    print("Inserting backfilled rows...")
    fg.insert(df)

    print("Backfill complete.")


if __name__ == "__main__":
    run_backfill(days_back=365, chunk_days=30)

