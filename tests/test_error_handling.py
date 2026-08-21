import pytest
from unittest.mock import patch, MagicMock

from feature_pipeline import fetch_data


def test_fetch_raises_valueerror_when_api_key_missing():
    """
    fetch_current_features() must raise a clear ValueError if the
    OpenWeather API key is missing, rather than proceeding and failing
    with a confusing downstream error.
    """
    with patch.object(fetch_data, "API_KEY", None):
        with pytest.raises(ValueError, match="OPENWEATHER_API_KEY not found"):
            fetch_data.fetch_current_features()

def test_fetch_raises_runtimeerror_on_weather_api_failure():
    """
    fetch_current_features() must raise a clear RuntimeError if the
    Weather API returns a non-200 status code, rather than crashing
    later with a confusing KeyError.
    """
    fake_response = MagicMock()
    fake_response.status_code = 401
    fake_response.text = "Invalid API key"

    with patch.object(fetch_data, "API_KEY", "fake_key_for_test"):
        with patch("feature_pipeline.fetch_data.requests.get", return_value=fake_response):
            with pytest.raises(RuntimeError, match="Weather API failed: 401"):
                fetch_data.fetch_current_features()


def test_fetch_raises_runtimeerror_on_pollution_api_failure():
    """
    fetch_current_features() must raise a clear RuntimeError if the
    Pollution API returns a non-200 status code, even when the Weather
    API call succeeds first.
    """
    good_weather_response = MagicMock()
    good_weather_response.status_code = 200
    good_weather_response.json.return_value = {
        "main": {"temp": 30, "humidity": 50, "pressure": 1000},
        "wind": {"speed": 2.0, "deg": 90},
    }

    bad_pollution_response = MagicMock()
    bad_pollution_response.status_code = 500
    bad_pollution_response.text = "Internal Server Error"

    with patch.object(fetch_data, "API_KEY", "fake_key_for_test"):
        with patch(
            "feature_pipeline.fetch_data.requests.get",
            side_effect=[good_weather_response, bad_pollution_response],
        ):
            with pytest.raises(RuntimeError, match="Pollution API failed: 500"):
                fetch_data.fetch_current_features()            