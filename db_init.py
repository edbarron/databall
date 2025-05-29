import sqlite3
from config import DB_PATH, SCHEMA_FILE

def initialize_database():
    try:
        # Connect to SQLite database (creates file if it doesn't exist)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Read SQL schema from file
        with open(SCHEMA_FILE, "r") as f:
            schema = f.read()

        # Execute the schema script
        cursor.executescript(schema)
        conn.commit()
        print(f"Database '{DB_PATH}' created and initialized successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    initialize_database()