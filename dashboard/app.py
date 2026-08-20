import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from explain_prediction import explain_single_prediction
from load_models import load_latest_models
from predict import get_latest_feature_row, generate_forecast
from aqi_labels import get_aqi_label

st.set_page_config(page_title="Rawalpindi AQI Forecast", page_icon="🌫️")


@st.cache_data(ttl=3600)
def get_background_sample():
    """
    Fetch a diverse sample of historical rows to use as a SHAP background
    dataset for the Ridge (linear) explainer. Cached for an hour since
    this doesn't need to be perfectly fresh.
    """
    from feature_pipeline.feature_store import get_feature_store, get_or_create_aqi_feature_group
    from feature_pipeline.lag_features import add_lag_features
    from training_pipeline.train import FEATURE_COLUMNS

    fs = get_feature_store()
    fg = get_or_create_aqi_feature_group(fs)
    raw_df = fg.read()
    enriched_df = add_lag_features(raw_df)
    return enriched_df[FEATURE_COLUMNS].dropna().sample(100, random_state=42)

def get_models():
    """Load models once per hour (cached as a resource, not re-downloaded every rerun)."""
    return load_latest_models()


@st.cache_data(ttl=600)
def get_forecast():
    """Fetch latest features and generate forecast, cached for 10 minutes."""
    models = get_models()
    latest_row = get_latest_feature_row()
    forecast = generate_forecast(models, latest_row)
    current_aqi = float(latest_row["aqi"].iloc[0])
    return forecast, current_aqi


st.title("🌫️ Rawalpindi AQI Forecast")
st.caption("3-day Air Quality Index forecast, powered by a serverless ML pipeline")

with st.spinner("Loading latest forecast..."):
    forecast, current_aqi = get_forecast()

current_label, current_emoji = get_aqi_label(current_aqi)
st.metric("Current AQI", f"{current_emoji} {current_label}", f"{current_aqi:.1f}")

st.subheader("Next 3 Days")
col1, col2, col3 = st.columns(3)

labels = ["Tomorrow", "In 2 days", "In 3 days"]
targets = ["target_1d", "target_2d", "target_3d"]

for col, label, target in zip([col1, col2, col3], labels, targets):
    value = forecast[target]
    category, emoji = get_aqi_label(value)
    with col:
        st.metric(label, f"{emoji} {category}", f"{value:.2f}")

st.subheader("Why these predictions?")

WINNERS = {
    "target_1d": "random_forest",
    "target_2d": "ridge",
    "target_3d": "ridge",
}
models = get_models()
latest_row = get_latest_feature_row()
background_sample = get_background_sample()

explain_tabs = st.tabs(["Tomorrow", "In 2 days", "In 3 days"])

for tab, target in zip(explain_tabs, targets):
    with tab:
        model_type = WINNERS[target]
        contributions = explain_single_prediction(
            models[target], model_type, latest_row, background_sample
        )

        top_5 = contributions.head(5)
        for feature, value in top_5.items():
            direction = "⬆️ increased" if value > 0 else "⬇️ decreased"
            st.write(f"**{feature}** {direction} the prediction by {abs(value):.3f}")

if st.button("🔄 Refresh forecast"):
    st.cache_data.clear()
    st.rerun()