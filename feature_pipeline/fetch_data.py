import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

from feature_pipeline.config import (
    CITY_NAME, LATITUDE, LONGITUDE, WEATHER_URL, POLLUTION_URL
)

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")


def fetch_current_features() -> dict:
    """
    Fetch current weather and air pollution data for the configured city,
    and merge them into a single flat feature row.

    Returns:
        dict: A flat dictionary containing weather + pollution features,
              plus city name and UTC timestamp.

    Raises:
        ValueError: if the API key is missing.
        RuntimeError: if either API call fails (non-200 response).
    """
    if not API_KEY:
        raise ValueError("OPENWEATHER_API_KEY not found. Check your .env file.")

    params_common = {"lat": LATITUDE, "lon": LONGITUDE, "appid": API_KEY}

    # --- Weather call ---
    weather_resp = requests.get(
        WEATHER_URL, params={**params_common, "units": "metric"}
    )
    if weather_resp.status_code != 200:
        raise RuntimeError(
            f"Weather API failed: {weather_resp.status_code} - {weather_resp.text}"
        )
    weather_data = weather_resp.json()

    # --- Pollution call ---
    pollution_resp = requests.get(POLLUTION_URL, params=params_common)
    if pollution_resp.status_code != 200:
        raise RuntimeError(
            f"Pollution API failed: {pollution_resp.status_code} - {pollution_resp.text}"
        )
    pollution_data = pollution_resp.json()["list"][0]

    # --- Merge into one flat row ---
    merged_row = {
        "city": CITY_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat(),

        "temperature": weather_data["main"]["temp"],
        "humidity": weather_data["main"]["humidity"],
        "pressure": weather_data["main"]["pressure"],
        "wind_speed": weather_data["wind"]["speed"],
        "wind_deg": weather_data["wind"].get("deg"),

        "aqi": pollution_data["main"]["aqi"],
        "co": pollution_data["components"]["co"],
        "no2": pollution_data["components"]["no2"],
        "so2": pollution_data["components"]["so2"],
        "o3": pollution_data["components"]["o3"],
        "pm2_5": pollution_data["components"]["pm2_5"],
        "pm10": pollution_data["components"]["pm10"],
        "nh3": pollution_data["components"]["nh3"],
    }

    return merged_row


if __name__ == "__main__":
    row = fetch_current_features()
    print(row)