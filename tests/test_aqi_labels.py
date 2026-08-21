from dashboard.aqi_labels import get_aqi_label, check_hazard_alerts


def test_get_aqi_label_normal_values():
    """Standard in-range values should map to the correct category."""
    assert get_aqi_label(1.0) == ("Good", "🟢")
    assert get_aqi_label(3.0) == ("Moderate", "🟠")
    assert get_aqi_label(5.0) == ("Very Poor", "🟣")


def test_get_aqi_label_rounds_correctly():
    """Fractional values should round to the nearest whole category."""
    assert get_aqi_label(3.4)[0] == "Moderate"  # rounds to 3
    assert get_aqi_label(3.6)[0] == "Poor"       # rounds to 4


def test_get_aqi_label_clamps_out_of_range_values():
    """
    Values outside 1-5 (which a regression model could theoretically
    produce) must be clamped, not raise a KeyError.
    """
    assert get_aqi_label(0.2)[0] == "Good"       # clamps to 1
    assert get_aqi_label(-1.0)[0] == "Good"      # clamps to 1
    assert get_aqi_label(6.5)[0] == "Very Poor"  # clamps to 5
    assert get_aqi_label(100)[0] == "Very Poor"  # clamps to 5


def test_check_hazard_alerts_no_hazard():
    """A forecast entirely below the threshold should return no warnings."""
    forecast = {"target_1d": 2.0, "target_2d": 3.0, "target_3d": 3.4}
    warnings = check_hazard_alerts(forecast)
    assert warnings == []


def test_check_hazard_alerts_detects_single_hazard_day():
    """Exactly one day crossing the threshold should produce one warning."""
    forecast = {"target_1d": 4.2, "target_2d": 2.0, "target_3d": 3.0}
    warnings = check_hazard_alerts(forecast)
    assert len(warnings) == 1
    assert "Tomorrow" in warnings[0]


def test_check_hazard_alerts_detects_multiple_hazard_days():
    """Multiple days crossing the threshold should each get a warning."""
    forecast = {"target_1d": 4.5, "target_2d": 5.0, "target_3d": 2.0}
    warnings = check_hazard_alerts(forecast)
    assert len(warnings) == 2


def test_check_hazard_alerts_boundary_value():
    """
    A value that rounds exactly to the threshold (4) should count as
    hazardous - the boundary itself is included, not excluded.
    """
    forecast = {"target_1d": 3.5, "target_2d": 3.0, "target_3d": 3.0}
    warnings = check_hazard_alerts(forecast)
    # 3.5 rounds to 4, which meets HAZARD_THRESHOLD (>= 4)
    assert len(warnings) == 1


def test_check_hazard_alerts_does_not_trigger_below_threshold():
    """
    A value that rounds down to 3 (just below the alert threshold)
    should NOT trigger an alert.
    """
    forecast = {"target_1d": 3.4, "target_2d": 2.0, "target_3d": 2.0}
    warnings = check_hazard_alerts(forecast)
    assert warnings == []