from app import create_app, db
from app.models.organization import Organization

app = create_app()
with app.app_context():
    org = Organization.query.first()
    if org:
        print(f"Org ID: {org.id}")
        print(f"API Key: {org.api_key}")
    else:
        print("No organization found")
