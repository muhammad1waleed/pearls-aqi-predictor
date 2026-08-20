from feature_pipeline.feature_store import get_feature_store, get_or_create_aqi_feature_group
from feature_pipeline.lag_features import add_lag_features
from training_pipeline.train import FEATURE_COLUMNS


def get_latest_feature_row():
    """
    Fetch all feature store data, recompute lag/rolling features, and
    return the single most recent row (as a DataFrame with one row),
    ready to feed into a model.

    Returns:
        pd.DataFrame: one-row DataFrame with all FEATURE_COLUMNS populated.
    """
    fs = get_feature_store()
    fg = get_or_create_aqi_feature_group(fs)

    raw_df = fg.read()
    enriched_df = add_lag_features(raw_df)

    latest_row = enriched_df.sort_values("timestamp", ascending=False).head(1)

    return latest_row[FEATURE_COLUMNS]


def generate_forecast(models: dict, latest_row) -> dict:
    """
    Run all 3 models against the latest feature row to produce a
    3-day AQI forecast.

    Args:
        models (dict): {"target_1d": model, "target_2d": model, "target_3d": model}
        latest_row (pd.DataFrame): one-row DataFrame of FEATURE_COLUMNS.

    Returns:
        dict: {"target_1d": prediction, "target_2d": prediction, "target_3d": prediction}
    """
    forecast = {}
    for target, model in models.items():
        prediction = model.predict(latest_row)[0]
        forecast[target] = round(float(prediction), 2)

    return forecast


if __name__ == "__main__":
    from dashboard.load_models import load_latest_models

    print("Loading models...")
    models = load_latest_models()

    print("Fetching latest feature row...")
    latest_row = get_latest_feature_row()
    print(latest_row)

    print("\nGenerating forecast...")
    forecast = generate_forecast(models, latest_row)
    print(forecast)