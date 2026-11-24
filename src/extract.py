"""
Extract module: Fetches live weather data from Open-Meteo API.
"""
from typing import Dict, List, Any
import requests
import pandas as pd

# Metadata for 3 Indian cities
CITIES: List[Dict[str, Any]] = [
    {"city_id": 1, "city_name": "Pune", "latitude": 18.5204, "longitude": 73.8567},
    {"city_id": 2, "city_name": "Mumbai", "latitude": 19.0760, "longitude": 72.8777},
    {"city_id": 3, "city_name": "Bengaluru", "latitude": 12.9716, "longitude": 77.5946},
]

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_cities_dataframe() -> pd.DataFrame:
    """Returns the cities dimension table as a DataFrame."""
    return pd.DataFrame(CITIES)


def fetch_weather_for_city(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Calls the Open-Meteo API for 24-hour hourly temperature and humidity.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m",
        "forecast_days": 1,
        "timezone": "Asia/Kolkata",
    }
    response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def extract_all_cities_weather() -> List[Dict[str, Any]]:
    """
    Fetches raw weather data for all configured cities.
    Returns a list of dictionaries containing city metadata and API payload.
    """
    extracted_data = []
    for city in CITIES:
        print(f"[EXTRACT] Fetching live weather for {city['city_name']}...")
        payload = fetch_weather_for_city(city["latitude"], city["longitude"])
        extracted_data.append({
            "city_id": city["city_id"],
            "city_name": city["city_name"],
            "payload": payload,
        })
    return extracted_data
