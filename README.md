# Weather Data Engineering Pipeline

A modular, lightweight Data Engineering ETL (Extract, Transform, Load) pipeline built in Python. The project extracts live 24-hour hourly weather data from the [Open-Meteo API](https://open-meteo.com/) for three Indian cities (**Pune**, **Mumbai**, and **Bengaluru**), enforces data quality and cleaning standards with pandas, persists the data to both columnar Parquet format and normalized SQLite tables, and performs aggregated analytical SQL queries.

---

## Architecture Overview

```
                      +-------------------------+
                      |     Open-Meteo API      |
                      +-------------------------+
                                   |
                             (JSON payload)
                                   v
                      +-------------------------+
                      |   1. EXTRACT (API)      |
                      |     src/extract.py      |
                      +-------------------------+
                                   |
                                   v
                      +-------------------------+
                      |  2. TRANSFORM & QA      |
                      |    src/transform.py     |
                      |  - Deduplication        |
                      |  - Null value removal   |
                      |  - Humidity bounds check|
                      +-------------------------+
                                   |
                    +--------------+--------------+
                    |                             |
                    v                             v
       +-------------------------+   +-------------------------+
       |   3a. Analytical Store  |   |  3b. Relational Store   |
       |  data/hourly_weather    |   |     data/weather.db     |
       |        .parquet         |   | - cities (dimension)    |
       |       (PyArrow)         |   | - hourly_weather (fact) |
       +-------------------------+   +-------------------------+
                                                  |
                                                  v
                                     +-------------------------+
                                     |    4. SQL Analytics     |
                                     |      src/query.py       |
                                     | (INNER JOIN + GROUP BY) |
                                     +-------------------------+
```

---

## Tech Stack

- **Language:** Python 3.10+
- **HTTP Client:** `requests` (Open-Meteo REST API)
- **Data Processing & QA:** `pandas`
- **Analytical Storage:** `pyarrow` (Apache Parquet)
- **Relational Storage:** `sqlite3`
- **Testing:** `pytest`

---

## Data Model

The pipeline creates both columnar analytical files and a normalized relational schema:

### 1. Relational Schema (`data/weather.db`)

- **Dimension Table: `cities`**
  - `city_id` (INTEGER, Primary Key): Unique city identifier (1: Pune, 2: Mumbai, 3: Bengaluru)
  - `city_name` (TEXT): City name
  - `latitude` (REAL): Geographical latitude
  - `longitude` (REAL): Geographical longitude

- **Fact Table: `hourly_weather`**
  - `city_id` (INTEGER, Foreign Key -> `cities.city_id`)
  - `time` (TEXT): ISO 8601 hourly timestamp
  - `temp_c` (REAL): Ambient temperature in Celsius (2m elevation)
  - `humidity` (REAL): Relative humidity percentage (validated between 0 and 100)

### 2. Analytical File (`data/hourly_weather.parquet`)

- Contains the combined, cleaned weather data stored in Apache Parquet format for fast columnar scans and high-compression analytical queries.

---

## Project Structure

```
WEATHER_PROJECT py/
├── data/                         # Pipeline storage (auto-created, git-ignored)
│   ├── weather.db                # SQLite database
│   └── hourly_weather.parquet    # Analytical Parquet file
├── src/
│   ├── __init__.py
│   ├── extract.py                # Live API data fetching
│   ├── transform.py              # Parsing, schema standardization, and QA rules
│   ├── load.py                   # Storage handlers (Parquet & SQLite)
│   └── query.py                  # Analytical SQL queries (JOIN + aggregation)
├── tests/
│   ├── __init__.py
│   └── test_transform.py         # Pytest unit tests using dummy JSON fixtures
├── main.py                       # Pipeline orchestrator
├── requirements.txt              # Production and test dependencies
├── .gitignore                    # Prevents checking in data, databases, and caches
└── README.md                     # Project documentation
```

---

## How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Execute the Pipeline

Run the end-to-end pipeline from the root directory:

```bash
python main.py
```

### 3. Run Unit Tests

Execute the unit test suite (runs offline with mock JSON payloads):

```bash
pytest
```

---

## Sample Output

When running `python main.py`, the console displays step-by-step progress followed by the analytical SQL summary:

```text
=================================================================
  WEATHER ETL PIPELINE: Pune, Mumbai, Bengaluru
=================================================================

[STEP 1/4] EXTRACT: Fetching live API weather data...
[EXTRACT] Fetching live weather for Pune...
[EXTRACT] Fetching live weather for Mumbai...
[EXTRACT] Fetching live weather for Bengaluru...

[STEP 2/4] TRANSFORM: Cleaning and validating data...
[TRANSFORM] Processed 72 clean hourly records.

[STEP 3/4] LOAD: Persisting data to Parquet & SQLite...
[LOAD] Successfully saved 72 records to Parquet: data\hourly_weather.parquet
[LOAD] Successfully loaded 'cities' (3 rows) and 'hourly_weather' (72 rows) into data\weather.db

[STEP 4/4] QUERY: Executing SQL analytical query...

=================================================================
        ANALYTICAL WEATHER SUMMARY (INNER JOIN + GROUP BY)
=================================================================
 city_name  recorded_hours  avg_temp_c  max_temp_c  min_temp_c  avg_humidity
 Bengaluru              24       22.15        28.4        17.9         68.42
    Mumbai              24       28.45        33.1        24.6         65.18
      Pune              24       24.80        31.2        18.5         54.25
=================================================================

[SUCCESS] Pipeline completed successfully!
```
