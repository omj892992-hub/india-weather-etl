"""
Load module: Stores cleaned weather data in Parquet and SQLite relational tables.
"""
import os
import sqlite3
import pandas as pd

DATA_DIR = "data"
PARQUET_PATH = os.path.join(DATA_DIR, "hourly_weather.parquet")
SQLITE_DB_PATH = os.path.join(DATA_DIR, "weather.db")


def ensure_data_dir() -> None:
    """Ensures the destination data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)


def save_to_parquet(df: pd.DataFrame, file_path: str = PARQUET_PATH) -> None:
    """
    Saves cleaned hourly weather data to an analytical Parquet file.
    """
    ensure_data_dir()
    df.to_parquet(file_path, index=False, engine="pyarrow")
    print(f"[LOAD] Successfully saved {len(df)} records to Parquet: {file_path}")


def save_to_sqlite(
    cities_df: pd.DataFrame,
    weather_df: pd.DataFrame,
    db_path: str = SQLITE_DB_PATH,
) -> None:
    """
    Saves data into two SQLite tables:
    - 'cities' (dimension table: city_id, city_name, latitude, longitude)
    - 'hourly_weather' (fact table: city_id, time, temp_c, humidity)
    """
    ensure_data_dir()
    conn = sqlite3.connect(db_path)
    try:
        # 1. Save cities dimension table
        cities_df.to_sql("cities", conn, if_exists="replace", index=False)

        # 2. Save hourly_weather fact table (normalized with foreign key city_id)
        fact_cols = ["city_id", "time", "temp_c", "humidity"]
        fact_df = weather_df[fact_cols]
        fact_df.to_sql("hourly_weather", conn, if_exists="replace", index=False)

        print(
            f"[LOAD] Successfully loaded 'cities' ({len(cities_df)} rows) and "
            f"'hourly_weather' ({len(fact_df)} rows) into {db_path}"
        )
    finally:
        conn.close()
