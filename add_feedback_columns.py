
from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Adding feedback columns to event table...")
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE event ADD COLUMN feedback VARCHAR(20)"))
            conn.execute(text("ALTER TABLE event ADD COLUMN feedback_at DATETIME"))
            conn.execute(text("ALTER TABLE event ADD COLUMN adjusted_score FLOAT"))
            conn.commit()
        print("Columns added successfully.")
    except Exception as e:
        print(f"Error (columns might already exist): {e}")
