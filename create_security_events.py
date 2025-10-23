import random
import time
from datetime import datetime
from app import create_app, db
from app.models.organization import Organization
from app.models.security_event import SecurityEvent

app = create_app()

EVENT_TYPES = [
    ("Failed Login Attempt", "warning"),
    ("Malware Detected", "critical"),
    ("Firewall Breach", "critical"),
    ("Suspicious File Uploaded", "warning"),
    ("Antivirus Scan Completed", "info"),
    ("User Password Changed", "info"),
    ("Unauthorized Access Blocked", "warning"),
    ("System Update Installed", "info"),
]

def generate_random_event():
    """Create a random event and assign it to a random organization."""
    with app.app_context():
        orgs = Organization.query.all()
        if not orgs:
            print("⚠️ No organizations found! Please seed the database first.")
            return
        
        org = random.choice(orgs)
        event_name, severity = random.choice(EVENT_TYPES)
        
        event = SecurityEvent(
            event_type=event_name,
            severity=severity,
            source_ip=f"192.168.1.{random.randint(10, 255)}",
            timestamp=datetime.utcnow(),
            organization_id=org.id,
            description=f"{event_name} detected in {org.name} sector.",
        )
        
        db.session.add(event)
        db.session.commit()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Event Added: {event_name} ({severity}) for {org.name}")

if __name__ == "__main__":
    print("🚀 Starting Security Event Generator...")
    try:
        while True:
            generate_random_event()
            time.sleep(random.randint(5, 15))  # generate every 5–15 seconds
    except KeyboardInterrupt:
        print("\n🛑 Event generator stopped manually.")
