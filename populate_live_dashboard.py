
import random
from datetime import datetime, timedelta, timezone
from app import create_app
from app.extensions import db
from app.models import Organization, Device, Alert, User

def populate_live_data():
    app = create_app()
    with app.app_context():
        print("Starting Live Dashboard Population...")

        # 1. Find the active user/org
        # Target the specific user we are debugging
        user = User.query.filter_by(email="testorg1@gmail.com").first()
        if not user:
            user = User.query.filter_by(email="admin@tenshiguard.ai").first()
        if not user:
            user = User.query.first()
        
        if not user:
            print("No user found. Please register first.")
            return

        org = user.organization
        if not org:
            print("No organization found for user.")
            return

        print(f"Target Organization: {org.name} (ID: {org.id})")

        # 2. Find the active device
        # We prioritize the one that was seen most recently
        device = Device.query.filter_by(organization_id=org.id).order_by(Device.last_seen.desc()).first()
        
        if not device:
            print("No devices found. Creating a simulated device for dashboard preview...")
            device = Device(
                organization_id=org.id,
                device_name="Simulated-PC",
                mac="00:00:00:00:00:01",
                os="Windows 11",
                ip="192.168.1.100",
                status="online",
                last_seen=datetime.now(timezone.utc)
            )
            db.session.add(device)
            db.session.commit()
            print(f"Created device: {device.device_name}")

        print(f"Target Device: {device.device_name} (IP: {device.ip}, OS: {device.os})")

        # 3. Generate "Failed Login" Events (High Severity, Auth Category)
        # Distributed over last 24 hours
        print("Injecting Failed Login events...")
        now = datetime.now(timezone.utc)
        
        for i in range(12):
            # Random time in last 24h
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

        # 4. Generate "Malware/Critical" Events
        print("Injecting Critical Security events...")
        for i in range(5):
            time_offset = random.randint(0, 24 * 60)
            event_time = now - timedelta(minutes=time_offset)
            
            alert = Alert(
                organization_id=org.id,
                device_id=device.id,
                title="Malware Detected",
                message="Trojan.Win32.Generic detected in C:\\Temp\\suspicious.exe",
                category="malware",
                severity="critical",
                created_at=event_time
            )
            db.session.add(alert)

        # 5. Generate "Network/Medium" Events
        print("Injecting Network events...")
        for i in range(8):
            time_offset = random.randint(0, 24 * 60)
            event_time = now - timedelta(minutes=time_offset)
            
            alert = Alert(
                organization_id=org.id,
                device_id=device.id,
                title="Port Scan Detected",
                message=f"Inbound connection attempt on port {random.choice([22, 3389, 445])}",
                category="network",
                severity="medium",
                created_at=event_time
            )
            db.session.add(alert)

        # 6. Generate "System/Info" Events
        print("Injecting System events...")
        for i in range(15):
            time_offset = random.randint(0, 24 * 60)
            event_time = now - timedelta(minutes=time_offset)
            
            alert = Alert(
                organization_id=org.id,
                device_id=device.id,
                title="Service Started",
                message="TenshiGuard Agent Service started successfully",
                category="system",
                severity="info",
                created_at=event_time
            )
            db.session.add(alert)

        # 7. Generate Device Telemetry (CPU/Mem) for Performance Chart
        # Generate data points for every hour in the last 24h
        print("Injecting Device Telemetry (CPU/RAM)...")
        from app.models.device_telemetry import DeviceTelemetry
        
        for i in range(24):
            # Time: i hours ago
            t = now - timedelta(hours=i)
            
            # Simulate some load pattern
            cpu = random.randint(10, 80)
            mem = random.randint(30, 90)
            
            telemetry = DeviceTelemetry(
                device_id=device.id,
                cpu_percent=cpu,
                mem_percent=mem,
                ts=t
            )
            db.session.add(telemetry)

        db.session.commit()
        print("Dashboard successfully populated with live event and telemetry data!")

if __name__ == "__main__":
    populate_live_data()
