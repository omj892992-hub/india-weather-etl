"""
Transform module: Parses, cleans, and validates weather data.
"""
from typing import List, Dict, Any
import pandas as pd


def parse_weather_payload(city_id: int, city_name: str, payload: Dict[str, Any]) -> pd.DataFrame:
    """
    Parses hourly weather array from raw API payload into a pandas DataFrame.
    """
    if "hourly" not in payload:
        raise ValueError("Invalid payload: 'hourly' key not found.")

    hourly = payload["hourly"]
    df = pd.DataFrame({
        "city_id": city_id,
        "city_name": city_name,
        "time": hourly.get("time", []),
        "temp_c": hourly.get("temperature_2m", []),
        "humidity": hourly.get("relative_humidity_2m", []),
    })
    return df


def clean_weather_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies data quality checks and cleaning rules:
    1. Removes duplicate records for the same city and timestamp.
    2. Drops rows with missing/null values in key columns.
    3. Type-casts metrics and handles non-numeric errors.
    4. Validates humidity range (0 to 100).
    """
    cleaned = df.copy()

    # 1. Deduplicate by city and timestamp
    initial_count = len(cleaned)
    cleaned = cleaned.drop_duplicates(subset=["city_id", "time"])
    dedup_dropped = initial_count - len(cleaned)
    if dedup_dropped > 0:
        print(f"[TRANSFORM] Dropped {dedup_dropped} duplicate record(s).")

    # 2. Drop rows with nulls in critical metrics
    cleaned = cleaned.dropna(subset=["city_id", "time", "temp_c", "humidity"])

    # 3. Type casting & coercion
    cleaned["temp_c"] = pd.to_numeric(cleaned["temp_c"], errors="coerce")
    cleaned["humidity"] = pd.to_numeric(cleaned["humidity"], errors="coerce")
    cleaned = cleaned.dropna(subset=["temp_c", "humidity"])

    # 4. Data Quality Check: Humidity must be between 0 and 100
    valid_humidity = (cleaned["humidity"] >= 0) & (cleaned["humidity"] <= 100)
    invalid_count = int((~valid_humidity).sum())
    if invalid_count > 0:
        print(f"[TRANSFORM] Filtered out {invalid_count} record(s) with invalid humidity.")
    cleaned = cleaned[valid_humidity]

    return cleaned


def transform_all(extracted_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Transforms extracted raw city payloads into a single cleaned DataFrame.
    """
    dfs = []
    for item in extracted_data:
        city_df = parse_weather_payload(item["city_id"], item["city_name"], item["payload"])
        dfs.append(city_df)

    combined_df = pd.concat(dfs, ignore_index=True)
    cleaned_df = clean_weather_data(combined_df)
    return cleaned_df
