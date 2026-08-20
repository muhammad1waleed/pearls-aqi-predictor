import pandas as pd
from datetime import datetime, timezone, timedelta

from feature_pipeline.lag_features import add_lag_features


def build_test_df(aqi_values: list, pm2_5_values: list, pm10_values: list) -> pd.DataFrame:
    """
    Build a controlled, hourly-spaced test DataFrame for a single city,
    given a list of AQI/PM2.5/PM10 values (one per hour, in order).
    """
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = []
    for i, (aqi, pm2_5, pm10) in enumerate(zip(aqi_values, pm2_5_values, pm10_values)):
        rows.append({
            "city": "TestCity",
            "timestamp": start + timedelta(hours=i),
            "aqi": aqi,
            "pm2_5": pm2_5,
            "pm10": pm10,
        })
    return pd.DataFrame(rows)


def test_aqi_lag_1h_shifts_by_one_row():
    """
    aqi_lag_1h for row N should equal the aqi value of row N-1.
    """
    df = build_test_df(
        aqi_values=[1, 2, 3, 4, 5],
        pm2_5_values=[10, 10, 10, 10, 10],
        pm10_values=[20, 20, 20, 20, 20],
    )

    result = add_lag_features(df)

    # First row has no previous hour -> NaN
    assert pd.isna(result.loc[0, "aqi_lag_1h"])
    # Row 1's lag_1h should equal row 0's aqi (1)
    assert result.loc[1, "aqi_lag_1h"] == 1
    # Row 4's lag_1h should equal row 3's aqi (4)
    assert result.loc[4, "aqi_lag_1h"] == 4


def test_aqi_change_rate_is_correct():
    """
    aqi_change_rate should equal current aqi minus aqi_lag_1h.
    """
    df = build_test_df(
        aqi_values=[2, 5, 3],
        pm2_5_values=[10, 10, 10],
        pm10_values=[20, 20, 20],
    )

    result = add_lag_features(df)

    # Row 1: aqi=5, lag_1h=2 -> change_rate should be 3
    assert result.loc[1, "aqi_change_rate"] == 3
    # Row 2: aqi=3, lag_1h=5 -> change_rate should be -2
    assert result.loc[2, "aqi_change_rate"] == -2


def test_rolling_mean_excludes_current_row():
    """
    aqi_rolling_mean_24h must NOT include the current row's own value —
    it should only average strictly previous hours (data leakage check).
    """
    # 25 hours: first 24 are all aqi=1, the 25th (current) row is aqi=100
    aqi_values = [1] * 24 + [100]
    pm2_5_values = [10] * 25
    pm10_values = [20] * 25

    df = build_test_df(aqi_values, pm2_5_values, pm10_values)
    result = add_lag_features(df)

    last_row_rolling_mean = result.loc[24, "aqi_rolling_mean_24h"]

    # If the current row (100) leaked into its own rolling average,
    # the mean would be pulled up. It should be exactly 1.0 (average
    # of the 24 previous hours, all value 1), NOT influenced by 100.
    assert last_row_rolling_mean == 1.0