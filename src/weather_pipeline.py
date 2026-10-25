
"""Weather Data Pipeline & Dashboard project."""


import logging
import os
import math
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text


# Logging configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Load database settings from the project's .env file
load_dotenv(PROJECT_ROOT / ".env")

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "weather_pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)

logger = logging.getLogger(__name__)

def get_database_engine():
    
    """Create a SQLAlchemy engine for the PostgreSQL database."""

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    if not all([db_user, db_password, db_host, db_port, db_name]):
        raise ValueError(
            "Database settings missing. Check the project's .env file."
        )

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=db_user,
        password=db_password,
        host=db_host,
        port=int(db_port),
        database=db_name,
        )

    return create_engine(database_url, pool_pre_ping=True)



def load_weather_to_database(df):
    """Load weather records into PostgreSQL without duplicate inserts."""

    engine = get_database_engine()

    try:
        database_df = df.rename(
            columns={
                "humidity_percent": "relative_humidity",
                "feels_like_c": "apparent_temperature_c",
            }
        ).copy()

        # Fields not currently provided by our API request
        # Ensure the API fields are available for database loading
        database_df["is_day"] = df["is_day"]
        database_df["precipitation_mm"] = df["precipitation_mm"]
        database_df["weather_code"] = df["weather_code"]

        records = database_df.to_dict(orient="records")

        insert_query = text("""
            INSERT INTO public.weather_data (
                city,
                temperature_c,
                relative_humidity,
                apparent_temperature_c,
                is_day,
                precipitation_mm,
                weather_code,
                wind_speed_kmh,
                weather_time
            )
            VALUES (
                :city,
                :temperature_c,
                :relative_humidity,
                :apparent_temperature_c,
                :is_day,
                :precipitation_mm,
                :weather_code,
                :wind_speed_kmh,
                :weather_time
            )
            ON CONFLICT (city, weather_time) DO NOTHING;
        """)

        with engine.begin() as connection:
            connection.execute(insert_query, records)

        logger.info(
            "Database load attempted for %s weather records.",
            len(records),
        )
        print(
            f"Database load completed. Records processed: {len(records)}"
        )

    finally:
        engine.dispose()





# Project ke main folder ka path
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Jin cities ka weather collect karna hai
CITIES = ["Islamabad", "Lahore", "Karachi", "Dubai", "London"]

# Open-Meteo API: API key ki zaroorat nahi
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"



def fetch_weather(city):
    """Fetch and validate current weather data for a city."""

    city_coordinates = {
        "Islamabad": (33.6844, 73.0479),
        "Lahore": (31.5204, 74.3587),
        "Karachi": (24.8607, 67.0011),
        "Dubai": (25.2048, 55.2708),
        "London": (51.5072, -0.1276),
    }

    latitude, longitude = city_coordinates[city]

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "wind_speed_10m,"
            "precipitation,"
            "weather_code,"
            "is_day"
        ),
        "timezone": "auto",
    }

    response = requests.get(
        WEATHER_API_URL,
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    weather = response.json()
    current = weather["current"]

    humidity = current["relative_humidity_2m"]
    temperature = current["temperature_2m"]
    wind_speed = current["wind_speed_10m"]
    precipitation = current["precipitation"]
    weather_code = current["weather_code"]
    is_day = current["is_day"]
    
    
    feels_like = current["apparent_temperature"]
    weather_time = current["time"]
    
    
    required_values = {
        "humidity": humidity,
        "temperature": temperature,
        "wind_speed": wind_speed,
        "feels_like": feels_like,
        "precipitation": precipitation,
        "weather_code": weather_code,
        "is_day": is_day,
        "weather_time": weather_time,
    }

    for field, value in required_values.items():
        if value is None:
            raise ValueError(
                f"Missing {field} value for {city}"
            )

        if field != "weather_time":
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(
                    f"Invalid {field} value for {city}: {value}"
                )



    if not 0 <= humidity <= 100:
        raise ValueError(f"Invalid humidity for {city}: {humidity}")

    if not -90 <= temperature <= 60:
        raise ValueError(f"Invalid temperature for {city}: {temperature}")

    if wind_speed < 0:
        raise ValueError(f"Invalid wind speed for {city}: {wind_speed}")
        
    if not -90 <= feels_like <= 70:
        raise ValueError(
            f"Invalid feels-like temperature for {city}: {feels_like}"
        )

    
    return {
        "city": city,
        "temperature_c": temperature,
        "humidity_percent": humidity,
        "feels_like_c": feels_like,
        "wind_speed_kmh": wind_speed,
        "precipitation_mm": precipitation,
        "weather_code": weather_code,
        "is_day": is_day,
        "weather_time": weather_time,
    }

def main():
    """Run the weather data pipeline."""

    print("Weather Data Pipeline started successfully!")
    logger.info("Weather Data Pipeline started successfully.")

    records = []

    for city in CITIES:
        try:
            weather_record = fetch_weather(city)
            records.append(weather_record)
            print(f"Weather fetched successfully: {city}")
            logger.info("Weather fetched successfully: %s", city)
            
        except (requests.RequestException, KeyError, ValueError) as error:
            print(f"Could not fetch weather for {city}: {error}")
            logger.error("Could not fetch weather for %s: %s", city, error)
            
    if records:
        
        df = pd.DataFrame(records)  # Records ko DataFrame mein convert karta hai
        # Convert weather_time from text to datetime format
        df["weather_time"] = pd.to_datetime(df["weather_time"])

        # Show the updated data type
        print("\nUpdated Weather Time Data Type:")
        print(df["weather_time"].dtype)

        # Save conversion information in log file
        logger.info("weather_time converted to datetime format.")

        duplicate_count = df.duplicated(subset=["city"]).sum()
        logger.info("Duplicate city records found: %s", duplicate_count)
        print(f"Duplicate city records: {duplicate_count}")
        
        missing_values = df.isnull().sum()
        logger.info("Missing values per column:\n%s", missing_values)
        print("\nMissing Values Per Column:")
        print(missing_values)
                        
        # Check data types after datetime conversion
        print("\nData Types:")
        print(df.dtypes)

        logger.info("Data types checked:\n%s", df.dtypes)
        
        
        # Data quality summary
        total_records = len(df)
        duplicate_city_count = df.duplicated(subset=["city"]).sum()
        duplicate_observation_count = df.duplicated(
            subset=["city", "weather_time"]
        ).sum()
        total_missing_values = df.isnull().sum().sum()

        print("\nData Quality Summary:")
        print(f"Total records: {total_records}")
        print(f"Duplicate city records: {duplicate_city_count}")
        print(f"Duplicate city-time records: {duplicate_observation_count}")
        print(f"Total missing values: {total_missing_values}")

        logger.info(
            "Data quality summary: records=%s, duplicate_cities=%s, "
            "duplicate_observations=%s, missing_values=%s",
            total_records,
            duplicate_city_count,
            duplicate_observation_count,
            total_missing_values,
        )


        print("\nWeather Data Preview:")
        print(df.to_string(index=False))

        output_dir = PROJECT_ROOT / "data"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "weather_data.csv"
        df.to_csv(output_file, index=False)
        
        
        # Load weather data into PostgreSQL
        try:
            load_weather_to_database(df)
        except Exception as error:
            logger.exception("Failed to load weather data into PostgreSQL")
            print(f"PostgreSQL load failed: {error}")

        
        
        # Save historical data without duplicate observations
        history_file = output_dir / "weather_history.csv"

        if history_file.exists():
            history_df = pd.read_csv(history_file)
            history_df["weather_time"] = pd.to_datetime(
                history_df["weather_time"]
            )
            combined_df = pd.concat(
                [history_df, df],
                ignore_index=True,
            )
        else:
            combined_df = df.copy()

        records_before = len(combined_df)

        combined_df = combined_df.drop_duplicates(
            subset=["city", "weather_time"],
            keep="first",
        )

        duplicates_skipped = records_before - len(combined_df)

        combined_df.to_csv(history_file, index=False)

        logger.info(
            "Historical data saved. Total records: %s, duplicates skipped: %s",
            len(combined_df),
            duplicates_skipped,
        )

        print(f"Historical data saved to: {history_file}")
        print(f"Duplicate historical records skipped: {duplicates_skipped}")
        print(f"Total historical records: {len(combined_df)}")
        print("Weather Data Pipeline completed successfully!")
        logger.info("Weather Data Pipeline completed successfully.")


if __name__ == "__main__":
    main()