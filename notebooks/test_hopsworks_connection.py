import os
import hopsworks
from dotenv import load_dotenv

load_dotenv()

HOPSWORKS_API_KEY = os.getenv("HOPSWORKS_API_KEY")

if not HOPSWORKS_API_KEY:
    raise ValueError("HOPSWORKS_API_KEY not found. Check your .env file.")

project = hopsworks.login(api_key_value=HOPSWORKS_API_KEY)

print("Connected to project:", project.name)

fs = project.get_feature_store()
print("Feature store retrieved:", fs)