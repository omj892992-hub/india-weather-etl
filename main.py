"""
Weather ETL Pipeline Orchestrator.
Coordinates Extract -> Transform -> Load -> Query end-to-end.
"""
import sys
from src.extract import get_cities_dataframe, extract_all_cities_weather
from src.transform import transform_all
from src.load import save_to_parquet, save_to_sqlite
from src.query import print_weather_summary


def run_pipeline() -> None:
    """Executes the complete ETL pipeline."""
    print("=" * 65)
    print("  WEATHER ETL PIPELINE: Pune, Mumbai, Bengaluru")
    print("=" * 65)

    try:
        # 1. EXTRACT: Fetch live weather data for 3 Indian cities
        print("\n[STEP 1/4] EXTRACT: Fetching live API weather data...")
        cities_df = get_cities_dataframe()
        raw_weather_data = extract_all_cities_weather()

        # 2. TRANSFORM: Clean, deduplicate, and validate data quality
        print("\n[STEP 2/4] TRANSFORM: Cleaning and validating data...")
        cleaned_weather_df = transform_all(raw_weather_data)
        print(f"[TRANSFORM] Processed {len(cleaned_weather_df)} clean hourly records.")

        # 3. LOAD: Save to analytical Parquet and relational SQLite tables
        print("\n[STEP 3/4] LOAD: Persisting data to Parquet & SQLite...")
        save_to_parquet(cleaned_weather_df)
        save_to_sqlite(cities_df, cleaned_weather_df)

        # 4. QUERY: Perform analytical SQL aggregation using INNER JOIN
        print("\n[STEP 4/4] QUERY: Executing SQL analytical query...")
        print_weather_summary()

        print("[SUCCESS] Pipeline completed successfully!")

    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    run_pipeline()
