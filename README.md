# Weather Data Pipeline & Dashboard

## Project Overview

This project collects current weather data for five cities using the Open-Meteo API. It processes and validates the data using Python and Pandas, saves the latest observations to CSV files, and maintains historical weather records while preventing duplicate observations.

The project is designed to demonstrate practical Data Engineering and Data Analytics concepts, including API integration, data validation, data quality checks, logging, and historical data storage.

## Technologies Used

- **Python 3.13** — Core programming language
- **Pandas** — Data processing and analysis
- **Requests** — Fetching weather data from the API
- **Open-Meteo API** — Current weather data source
- **Logging** — Tracking pipeline execution and errors
- **CSV** — Storing latest and historical weather data
- **Git & GitHub** — Version control and project collaboration
- 

## Key Features

- Fetches current weather data for Islamabad, Lahore, Karachi, Dubai, and London.
- Processes API responses using Pandas DataFrames.
- Validates temperature, humidity, wind speed, and feels-like temperature.
- Checks for missing values and duplicate observations.
- Converts weather timestamps into datetime format.
- Saves the latest weather observations to `data/weather_data.csv`.
- Maintains historical records in `data/weather_history.csv`.
- Prevents duplicate historical observations using city and weather timestamp.
- Records pipeline execution and data quality information in log files.


## How to Run the Project

### 1. Clone the Repository

```bash
git clone <your-github-repository-url>
cd Whether-Data-Pipeline
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
python -m pip install pandas requests
```

### 5. Run the Pipeline

```bash
python src/weather_pipeline.py
```

The pipeline fetches current weather data, validates the records, saves CSV files, and logs execution details.


