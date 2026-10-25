
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

if not all([db_user, db_password, db_host, db_port, db_name]):
    raise ValueError("Database settings missing. Check your .env file.")


from sqlalchemy import URL

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=db_user,
    password=db_password,
    host=db_host,
    port=int(db_port),
    database=db_name,
)


engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    result = connection.execute(text("SELECT current_database(), current_user"))
    database, user = result.fetchone()
    print("Database connection successful!")
    print("Database:", database)
    print("User:", user)

engine.dispose()
