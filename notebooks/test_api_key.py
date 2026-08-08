import os
import requests
from dotenv import load_dotenv

# Load variables from .env into the environment
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    raise ValueError("OPENWEATHER_API_KEY not found. Check your .env file.")

# Rawalpindi coordinates
LAT = 33.6007
LON = 73.0679

url = "https://api.openweathermap.org/data/2.5/weather"
params = {
    "lat": LAT,
    "lon": LON,
    "appid": API_KEY,
    "units": "metric"
}

response = requests.get(url, params=params)

print("Status code:", response.status_code)
print("Response:", response.json())