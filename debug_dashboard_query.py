
from app import create_app
from app.extensions import db
from app.models import Event
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

app = create_app()

with app.app_context():
    print("Running dashboard query debug...")
    try:
        # Mock org_id - get the first org found or hardcode 1
        # We need an org that has events
        from app.models import Organization
        org = Organization.query.first()
        if not org:
            print("No organization found.")
            exit()
        
        org_id = org.id
        print(f"Using Org ID: {org_id}")

        now = datetime.now(timezone.utc)
        window_24h = now - timedelta(hours=24)

        # The query from api_dashboard.py
        query = db.session.query(
            func.strftime("%H:00", Event.ts).label("bucket"),
            func.count(Event.id).label("count"),
        ).filter(
            Event.organization_id == org_id,
            Event.category == "auth",
            Event.ts >= window_24h,
        ).group_by("bucket").order_by("bucket")
        
        print("Generated SQL:", str(query.statement.compile(db.engine)))
        
        rows = query.all()
        
        print("Query successful!")
        print("Rows:", rows)
        
        points = [{"bucket": r.bucket, "count": r.count} for r in rows]
        print("Points:", points)

    except Exception as e:
        print("Query FAILED:")
        print(e)
        import traceback
        traceback.print_exc()
