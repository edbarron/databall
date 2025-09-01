import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")  # loads only if present

DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "databall.db"))
SCHEMA_FILE = str(BASE_DIR / "schema.sql")
API_KEY = os.getenv("API_KEY") 
