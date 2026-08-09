import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    raise ValueError("OPENWEATHER_API_KEY not found. Check your .env file.")

LAT = 33.6007
LON = 73.0679

# --- Call 1: Weather ---
weather_url = "https://api.openweathermap.org/data/2.5/weather"
weather_params = {"lat": LAT, "lon": LON, "appid": API_KEY, "units": "metric"}
weather_resp = requests.get(weather_url, params=weather_params).json()

# --- Call 2: Air Pollution ---
pollution_url = "http://api.openweathermap.org/data/2.5/air_pollution"
pollution_params = {"lat": LAT, "lon": LON, "appid": API_KEY}
pollution_resp = requests.get(pollution_url, params=pollution_params).json()

# --- Merge into one flat row ---
pollution_data = pollution_resp["list"][0]

merged_row = {
    "city": "Rawalpindi",
    "timestamp": datetime.now(timezone.utc).isoformat(),

    # Weather features
    "temperature": weather_resp["main"]["temp"],
    "humidity": weather_resp["main"]["humidity"],
    "pressure": weather_resp["main"]["pressure"],
    "wind_speed": weather_resp["wind"]["speed"],
    "wind_deg": weather_resp["wind"].get("deg"),

    # Pollution features
    "aqi": pollution_data["main"]["aqi"],
    "co": pollution_data["components"]["co"],
    "no2": pollution_data["components"]["no2"],
    "so2": pollution_data["components"]["so2"],
    "o3": pollution_data["components"]["o3"],
    "pm2_5": pollution_data["components"]["pm2_5"],
    "pm10": pollution_data["components"]["pm10"],
    "nh3": pollution_data["components"]["nh3"],
}

print(merged_row)