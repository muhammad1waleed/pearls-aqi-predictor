import os
import joblib

import hopsworks
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

HOPSWORKS_API_KEY = os.getenv("HOPSWORKS_API_KEY") or st.secrets.get("HOPSWORKS_API_KEY")

MODEL_NAMES = {
    "target_1d": "aqi_target_1d_random_forest",
    "target_2d": "aqi_target_2d_ridge",
    "target_3d": "aqi_target_3d_ridge",
}


def load_latest_models() -> dict:
    """
    Connect to the Hopsworks Model Registry and download the latest
    version of each of our 3 AQI forecast models.

    Returns:
        dict: {"target_1d": model, "target_2d": model, "target_3d": model}
    """
    if not HOPSWORKS_API_KEY:
        raise ValueError("HOPSWORKS_API_KEY not found. Check your .env file.")

    project = hopsworks.login(api_key_value=HOPSWORKS_API_KEY)
    mr = project.get_model_registry()

    models = {}
    for target, model_name in MODEL_NAMES.items():
        all_versions = mr.get_models(model_name)
        latest_version = max(m.version for m in all_versions)
        registry_model = mr.get_model(model_name, version=latest_version)

        model_dir = registry_model.download()
        model_path = os.path.join(model_dir, f"{target}_model.pkl")
        models[target] = joblib.load(model_path)
        print(f"Loaded {model_name} version {registry_model.version}")

    return models


if __name__ == "__main__":
    loaded = load_latest_models()
    print(loaded)