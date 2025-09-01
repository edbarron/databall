# db_init.py
import sqlite3
from config import DB_PATH, SCHEMA_FILE

def initialize_database():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            schema = f.read()
        conn.executescript(schema)
        conn.commit()
        print(f"Database '{DB_PATH}' created and initialized successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    initialize_database()
