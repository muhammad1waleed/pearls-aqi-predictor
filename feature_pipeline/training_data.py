import pandas as pd

from feature_pipeline.lag_features import add_lag_features


def build_training_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare a full training-ready dataset from raw feature store data:
    adds lag features, adds forward-looking targets, and drops rows
    that are missing required lag or target values.

    Args:
        df (pd.DataFrame): Raw rows from the feature store (must contain
            'city', 'timestamp', 'aqi').

    Returns:
        pd.DataFrame: Cleaned, training-ready dataset.
    """
    df = add_lag_features(df)

    df["target_1d"] = df.groupby("city")["aqi"].shift(-24)
    df["target_2d"] = df.groupby("city")["aqi"].shift(-48)
    df["target_3d"] = df.groupby("city")["aqi"].shift(-72)

    required_columns = [
        "aqi_lag_1h", "aqi_lag_24h", "aqi_lag_48h", "aqi_lag_72h",
        "aqi_rolling_mean_24h", "pm2_5_rolling_mean_24h", "pm10_rolling_mean_24h",
        "target_1d", "target_2d", "target_3d",
    ]
    df = df.dropna(subset=required_columns).reset_index(drop=True)

    return df