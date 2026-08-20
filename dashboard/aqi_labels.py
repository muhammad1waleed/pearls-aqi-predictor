AQI_CATEGORIES = {
    1: ("Good", "🟢"),
    2: ("Fair", "🟡"),
    3: ("Moderate", "🟠"),
    4: ("Poor", "🔴"),
    5: ("Very Poor", "🟣"),
}


def get_aqi_label(aqi_value: float) -> tuple:
    """
    Convert a (possibly fractional) predicted AQI value into a
    human-readable category label and emoji indicator.

    Args:
        aqi_value (float): predicted AQI, typically between 1 and 5.

    Returns:
        (str, str): (category label, emoji)
    """
    rounded = round(aqi_value)
    rounded = max(1, min(5, rounded))  # clamp to valid 1-5 range
    return AQI_CATEGORIES[rounded]

HAZARD_THRESHOLD = 4  # category 4 ("Poor") or higher triggers an alert


def check_hazard_alerts(forecast: dict) -> list:
    """
    Check a forecast dict for any day predicted to cross the hazard
    threshold.

    Args:
        forecast (dict): {"target_1d": value, "target_2d": value, "target_3d": value}

    Returns:
        list: human-readable warning strings, one per hazardous day.
            Empty list if no day crosses the threshold.
    """
    day_labels = {
        "target_1d": "Tomorrow",
        "target_2d": "In 2 days",
        "target_3d": "In 3 days",
    }

    warnings = []
    for target, value in forecast.items():
        if round(value) >= HAZARD_THRESHOLD:
            category, emoji = get_aqi_label(value)
            warnings.append(f"{emoji} {day_labels[target]}: predicted AQI is {category} ({value:.2f})")

    return warnings