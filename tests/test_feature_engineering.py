from datetime import datetime, timezone

from feature_pipeline.feature_engineering import add_time_features


def test_add_time_features_extracts_correct_values():
    """
    Given a row with a known timestamp, add_time_features should
    correctly extract hour, day_of_week, and month.
    """
    # Tuesday, August 18, 2026, 09:30 UTC
    row = {
        "timestamp": datetime(2026, 8, 18, 9, 30, tzinfo=timezone.utc)
    }

    result = add_time_features(row)

    assert result["hour"] == 9
    assert result["day_of_week"] == 1  # Monday=0, so Tuesday=1
    assert result["month"] == 8


def test_add_time_features_preserves_existing_keys():
    """
    add_time_features should add new keys without removing or
    modifying existing ones.
    """
    row = {
        "timestamp": datetime(2026, 8, 18, 9, 30, tzinfo=timezone.utc),
        "city": "Rawalpindi",
        "aqi": 3,
    }

    result = add_time_features(row)

    assert result["city"] == "Rawalpindi"
    assert result["aqi"] == 3