
import random
from datetime import datetime, timedelta, timezone
from app import create_app
from app.extensions import db
from app.models import Device, Alert

def inject_for_sam():
    app = create_app()
    with app.app_context():
        print("Injecting events for device 'sam'...")
        
        # Find the specific live device
        device = Device.query.filter_by(device_name="sam").first()
        if not device:
            print("Device 'sam' not found!")
            return

        print(f"Found device: {device.device_name} (ID: {device.id})")
        org_id = device.organization_id
        now = datetime.now(timezone.utc)

        # 1. A resolved malware scan (looks good)
        alert = Alert(
            organization_id=org_id,
            device_id=device.id,
            title="Malware Scan Completed",
            message="Full system scan completed. No threats found.",
            category="system",
            severity="info",
            created_at=now - timedelta(minutes=5)
        )
        db.session.add(alert)

        # 2. Some network activity
        for i in range(3):
            alert = Alert(
                organization_id=org_id,
                device_id=device.id,
                title="Outbound Connection",
                message=f"Allowed connection to remote host 104.21.55.{random.randint(1, 255)}",
                category="network",
                severity="info",
                created_at=now - timedelta(minutes=random.randint(10, 60))
            )
            db.session.add(alert)

        # 3. A 'High' severity event to make it interesting (e.g. Policy Violation)
        alert = Alert(
            organization_id=org_id,
            device_id=device.id,
            title="Policy Violation",
            message="Attempted to run unauthorized application 'miner.exe'",
            category="process",
            severity="high",
            created_at=now - timedelta(hours=2)
        )
        db.session.add(alert)

        db.session.commit()
        print("Events injected for 'sam'!")

if __name__ == "__main__":
    inject_for_sam()
