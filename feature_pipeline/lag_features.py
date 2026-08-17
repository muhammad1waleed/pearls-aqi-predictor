import pandas as pd


def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add lag-based, change-rate, and rolling-average features to a
    DataFrame of historical AQI readings. Assumes roughly hourly-spaced
    data for a single city.

    Args:
        df (pd.DataFrame): Feature rows, must contain 'city', 'timestamp',
            'aqi', 'pm2_5', 'pm10'.

    Returns:
        pd.DataFrame: Same data, sorted by timestamp, with new columns:
            - aqi_lag_1h, aqi_lag_24h, aqi_lag_48h, aqi_lag_72h
            - aqi_change_rate
            - aqi_rolling_mean_24h
            - pm2_5_rolling_mean_24h
            - pm10_rolling_mean_24h
    """
    df = df.sort_values("timestamp").reset_index(drop=True)

    grouped = df.groupby("city")

    df["aqi_lag_1h"] = grouped["aqi"].shift(1)
    df["aqi_lag_24h"] = grouped["aqi"].shift(24)
    df["aqi_lag_48h"] = grouped["aqi"].shift(48)
    df["aqi_lag_72h"] = grouped["aqi"].shift(72)

    df["aqi_change_rate"] = df["aqi"] - df["aqi_lag_1h"]

    # Rolling averages: mean over the past 24 hours, shifted by 1 so the
    # current row's own value doesn't leak into its own rolling average
    df["aqi_rolling_mean_24h"] = (
        grouped["aqi"].transform(lambda s: s.shift(1).rolling(window=24).mean())
    )
    df["pm2_5_rolling_mean_24h"] = (
        grouped["pm2_5"].transform(lambda s: s.shift(1).rolling(window=24).mean())
    )
    df["pm10_rolling_mean_24h"] = (
        grouped["pm10"].transform(lambda s: s.shift(1).rolling(window=24).mean())
    )

    return df