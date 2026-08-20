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