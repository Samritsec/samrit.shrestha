import sqlite3
import os
from datetime import datetime

db_path = os.path.join("instance", "tenshiguard.db")

def add_column(cursor, table, col_def):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_def}")
        print(f"Added column: {col_def}")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print(f"Column already exists: {col_def}")
        else:
            print(f"Error adding {col_def}: {e}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    add_column(cursor, "device", "risk_score INTEGER DEFAULT 0")
    add_column(cursor, "device", "last_risk_update TIMESTAMP")
    
    conn.commit()
    conn.close()
    print("Database updated successfully.")
else:
    print(f"Database not found at {db_path}")
