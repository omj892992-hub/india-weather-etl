"""
Unit tests for weather transformation and data quality checks.
Uses small dummy JSON data with zero external API calls.
"""
import pytest
import pandas as pd
from src.transform import parse_weather_payload, clean_weather_data


@pytest.fixture
def sample_api_payload():
    """Dummy Open-Meteo payload with 3 hourly records."""
    return {
        "hourly": {
            "time": ["2026-11-24T00:00", "2026-11-24T01:00", "2026-11-24T02:00"],
            "temperature_2m": [22.5, 21.0, 20.2],
            "relative_humidity_2m": [65, 70, 75],
        }
    }


def test_parse_and_clean_valid_data(sample_api_payload):
    """
    Test 1: Validates that raw payload is correctly parsed into a DataFrame
    and all clean records are preserved.
    """
    df = parse_weather_payload(city_id=1, city_name="Pune", payload=sample_api_payload)
    cleaned = clean_weather_data(df)

    assert len(cleaned) == 3
    assert list(cleaned.columns) == ["city_id", "city_name", "time", "temp_c", "humidity"]
    assert cleaned["city_name"].iloc[0] == "Pune"
    assert cleaned["temp_c"].iloc[0] == 22.5
    assert cleaned["humidity"].iloc[0] == 65


def test_quality_checks_filter_invalid_humidity_and_duplicates():
    """
    Test 2: Validates data quality checks:
    - Removes duplicate timestamps for the same city.
    - Filters out invalid humidity values (< 0 or > 100).
    - Drops null values.
    """
    dirty_data = pd.DataFrame({
        "city_id": [1, 1, 1, 1, 1, 1],
        "city_name": ["Pune", "Pune", "Pune", "Pune", "Pune", "Pune"],
        "time": [
            "2026-11-24T00:00",
            "2026-11-24T00:00",  # Duplicate timestamp
            "2026-11-24T01:00",  # Invalid humidity > 100
            "2026-11-24T02:00",  # Invalid negative humidity < 0
            None,                # Null timestamp
            "2026-11-24T03:00",  # Valid record
        ],
        "temp_c": [22.0, 22.0, 23.5, 24.0, 20.0, 21.5],
        "humidity": [60, 60, 115, -15, 60, 55],
    })

    cleaned = clean_weather_data(dirty_data)

    # Only rows 0 and 5 should survive
    assert len(cleaned) == 2
    assert set(cleaned["time"]) == {"2026-11-24T00:00", "2026-11-24T03:00"}
    # Assert all remaining humidity values are strictly within [0, 100]
    assert (cleaned["humidity"] >= 0).all() and (cleaned["humidity"] <= 100).all()
