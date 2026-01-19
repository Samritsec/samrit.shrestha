import os
import psycopg2

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("No DATABASE_URL set")
    exit(1)

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cur.fetchall()
    print("Tables in DB:")
    for t in tables:
        print(f"- {t[0]}")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
