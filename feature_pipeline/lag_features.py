import pandas as pd


def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add lag-based and change-rate features to a DataFrame of historical
    AQI readings. Assumes roughly hourly-spaced data for a single city.

    Args:
        df (pd.DataFrame): Feature rows, must contain 'city', 'timestamp', 'aqi'.

    Returns:
        pd.DataFrame: Same data, sorted by timestamp, with new columns:
            - aqi_lag_1h: AQI value 1 row (≈1 hour) earlier
            - aqi_lag_24h: AQI value 24 rows (≈24 hours) earlier
            - aqi_change_rate: difference between current AQI and aqi_lag_1h
    """
    # Sort oldest -> newest so shift() looks "backward in time" correctly
    df = df.sort_values("timestamp").reset_index(drop=True)

    df["aqi_lag_1h"] = df.groupby("city")["aqi"].shift(1)
    df["aqi_lag_24h"] = df.groupby("city")["aqi"].shift(24)

    df["aqi_change_rate"] = df["aqi"] - df["aqi_lag_1h"]

    return df