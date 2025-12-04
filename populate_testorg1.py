
import random
from datetime import datetime, timedelta, timezone
from app import create_app
from app.extensions import db
from app.models import Organization, Device, Alert, User

def populate_testorg1():
    app = create_app()
    with app.app_context():
        print("Starting Population for testorg1...")

        # 1. Find the specific user
        user = User.query.filter_by(email="testorg1@gmail.com").first()
        if not user:
            print("User testorg1@gmail.com not found.")
            return

        org = user.organization
        if not org:
            print("No organization found for user.")
            return

        print(f"Target Organization: {org.name} (ID: {org.id})")

        # 2. Find the active device for this org
        device = Device.query.filter_by(organization_id=org.id).order_by(Device.last_seen.desc()).first()
        
        if not device:
            print("No devices found for this organization. Creating a mock one...")
            device = Device(
                organization_id=org.id,
                device_name="TestOrg1-PC",
                os="Windows 11 Enterprise",
                ip="192.168.50.10",
                mac="AA:BB:CC:DD:EE:FF",
                status="online",
                last_seen=datetime.now(timezone.utc)
            )
            db.session.add(device)
            db.session.commit()
            print(f"Created mock device: {device.device_name}")
        else:
            print(f"Target Device: {device.device_name} (IP: {device.ip})")

        # 3. Inject Events
        print("Injecting events...")
        now = datetime.now(timezone.utc)
        
        # Failed Logins
        for i in range(15):
            time_offset = random.randint(0, 24 * 60)
            event_time = now - timedelta(minutes=time_offset)
            alert = Alert(
                organization_id=org.id,
                device_id=device.id,
                title="Failed Login Attempt",
                message=f"Failed login for user 'admin' from {device.ip}",
                category="auth",
                severity="high",
                created_at=event_time
            )
            db.session.add(alert)

        # Critical Malware
        for i in range(3):
            time_offset = random.randint(0, 24 * 60)
            event_time = now - timedelta(minutes=time_offset)
            alert = Alert(
                organization_id=org.id,
                device_id=device.id,
                title="Ransomware Blocked",
                message="WannaCry signature detected and blocked.",
                category="malware",
                severity="critical",
                created_at=event_time
            )
            db.session.add(alert)

        # Network Scans
        for i in range(10):
            time_offset = random.randint(0, 24 * 60)
            event_time = now - timedelta(minutes=time_offset)
            alert = Alert(
                organization_id=org.id,
                device_id=device.id,
                title="Suspicious Outbound Traffic",
                message="Connection to known C2 server blocked.",
                category="network",
                severity="medium",
                created_at=event_time
            )
            db.session.add(alert)

        db.session.commit()
        print("Success! Dashboard populated for testorg1.")

if __name__ == "__main__":
    populate_testorg1()
