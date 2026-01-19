import os
import psycopg2

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("No DATABASE_URL set")
    exit(1)

try:
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()
    
    print("Dropping schema public...")
    cur.execute("DROP SCHEMA public CASCADE;")
    cur.execute("CREATE SCHEMA public;")
    cur.execute("GRANT ALL ON SCHEMA public TO public;")
    print("Schema reset complete.")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
