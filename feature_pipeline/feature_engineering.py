from datetime import datetime


def add_time_features(row: dict) -> dict:
    """
    Add time-based derived features to a single feature row, based on
    its 'timestamp' field (expected in ISO 8601 format, UTC).

    Args:
        row (dict): A feature row containing a 'timestamp' key.

    Returns:
        dict: The same row, with 'hour', 'day_of_week', and 'month' added.
    """
    dt = datetime.fromisoformat(row["timestamp"])

    row["hour"] = dt.hour
    row["day_of_week"] = dt.weekday()  # Monday=0 ... Sunday=6
    row["month"] = dt.month

    return row