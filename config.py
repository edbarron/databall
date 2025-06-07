import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the SQLite database
DB_PATH = os.path.join(BASE_DIR, "databall.db")

# Path to the schema.sql file
SCHEMA_FILE = os.path.join(BASE_DIR, "schema.sql")

# API key for API-Football (replace with your real key)
API_KEY = "96f21d098a774f81a724d17de03d90af" #your-api-key-here
