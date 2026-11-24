"""
Query module: Runs analytical SQL queries with INNER JOIN and GROUP BY on SQLite database.
"""
import sqlite3
import pandas as pd
from src.load import SQLITE_DB_PATH


def query_weather_summary(db_path: str = SQLITE_DB_PATH) -> pd.DataFrame:
    """
    Executes an analytical SQL query joining 'hourly_weather' and 'cities',
    calculating average temperature, max temperature, min temperature, and average humidity per city.
    """
    query = """
    SELECT
        c.city_name,
        COUNT(w.time) AS recorded_hours,
        ROUND(AVG(w.temp_c), 2) AS avg_temp_c,
        ROUND(MAX(w.temp_c), 2) AS max_temp_c,
        ROUND(MIN(w.temp_c), 2) AS min_temp_c,
        ROUND(AVG(w.humidity), 2) AS avg_humidity
    FROM hourly_weather w
    INNER JOIN cities c ON w.city_id = c.city_id
    GROUP BY c.city_name
    ORDER BY c.city_name;
    """

    conn = sqlite3.connect(db_path)
    try:
        summary_df = pd.read_sql_query(query, conn)
        return summary_df
    finally:
        conn.close()


def print_weather_summary(db_path: str = SQLITE_DB_PATH) -> None:
    """Runs the analytical query and prints a clean report."""
    summary = query_weather_summary(db_path)
    print("\n" + "=" * 65)
    print("        ANALYTICAL WEATHER SUMMARY (INNER JOIN + GROUP BY)")
    print("=" * 65)
    print(summary.to_string(index=False))
    print("=" * 65 + "\n")
