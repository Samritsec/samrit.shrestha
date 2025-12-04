import random
from datetime import datetime, timedelta, timezone
from app import create_app, db
from app.models.user import User
from app.models.device import Device
from app.models.alert import Alert
from app.models.ai_signal import AISignal
from app.models.event import Event

def simulate_attacks():
    app = create_app()
    with app.app_context():
        print("--- Starting Attack Simulation ---")
        
        # 1. Target User & Organization
        user = User.query.filter_by(email="testorg1@gmail.com").first()
        if not user:
            print("Error: User 'testorg1@gmail.com' not found.")
            return

        org_id = user.organization_id
        print(f"Target Org ID: {org_id}")

        # 2. Target Device (Prefer real agent, fallback to Simulated-PC)
        device = Device.query.filter_by(organization_id=org_id).order_by(Device.last_seen.desc()).first()
        if not device:
            print("Error: No device found for this organization.")
            return
        
        print(f"Target Device: {device.device_name} (ID: {device.id})")

        now = datetime.now(timezone.utc)
        
        # --- Attack Scenarios ---
        
        scenarios = [
            {
                "phase": "Reconnaissance",
                "alerts": [
                    ("network", "medium", "Port Scan Detected", "Multiple connection attempts on closed ports from 192.168.1.50"),
                    ("network", "low", "Unusual Outbound Traffic", "Connection to unknown external IP 45.33.22.11")
                ],
                "ai_signal": ("network", "Port Scanning Pattern", "medium", "Rapid sequence of SYN packets detected")
            },
            {
                "phase": "Initial Access",
                "alerts": [
                    ("auth", "high", "Failed Login Attempt", "Multiple failed RDP login attempts from 10.0.0.5"),
                    ("auth", "high", "Failed Login Attempt", "Failed SSH login for user 'admin'"),
                    ("auth", "critical", "Brute Force Detected", "50+ failed login attempts in 1 minute")
                ],
                "ai_signal": ("identity", "Brute Force Anomaly", "high", "High velocity authentication failures detected")
            },
            {
                "phase": "Execution",
                "alerts": [
                    ("process", "critical", "Malware Detected", "Windows Defender blocked 'trojan_win32.exe'"),
                    ("process", "high", "Suspicious PowerShell", "PowerShell executed with -EncodedCommand parameter")
                ],
                "ai_signal": ("process", "Malicious Script Execution", "critical", "Obfuscated PowerShell command identified")
            },
            {
                "phase": "Persistence",
                "alerts": [
                    ("system", "medium", "New Service Installed", "Service 'UpdaterService_v2' installed from temp directory"),
                    ("system", "high", "Registry Modification", "Run key modified for persistence: HKCU\\...\\Run")
                ],
                "ai_signal": ("host", "Persistence Mechanism", "high", "Unusual startup item added to registry")
            },
            {
                "phase": "Exfiltration",
                "alerts": [
                    ("network", "high", "Data Exfiltration Suspected", "Large upload (500MB) to unknown cloud storage"),
                    ("network", "critical", "C2 Communication", "Beaconing traffic detected to known C2 IP")
                ],
                "ai_signal": ("network", "Data Exfiltration", "critical", "Anomalous outbound data transfer volume")
            }
        ]

        # Inject Data
        for i, scenario in enumerate(scenarios):
            # Time offset: spread over the last hour
            time_offset = timedelta(minutes=10 * (len(scenarios) - i)) 
            event_time = now - time_offset
            
            print(f"Simulating Phase: {scenario['phase']}...")
            
            # Create Alerts
            for category, severity, title, detail in scenario['alerts']:
                alert = Alert(
                    organization_id=org_id,
                    device_id=device.id,
                    title=title,
                    message=detail,
                    category=category,
                    severity=severity,
                    created_at=event_time + timedelta(seconds=random.randint(0, 30))
                )
                db.session.add(alert)
            
            # Create AI Signal
            if "ai_signal" in scenario:
                cat, rule, severity, detail = scenario['ai_signal']
                
                # Generate a mitigation strategy based on the rule
                mitigation = "Investigate immediately."
                if "Port" in rule: mitigation = "Block source IP at firewall and review open ports."
                elif "Brute" in rule: mitigation = "Lock user account and enforce MFA."
                elif "Malicious" in rule: mitigation = "Isolate device and run full AV scan."
                elif "Persistence" in rule: mitigation = "Remove registry key and check for scheduled tasks."
                elif "Exfiltration" in rule: mitigation = "Block destination IP and revoke user credentials."

                signal = AISignal(
                    organization_id=org_id,
                    device_id=device.id,
                    category=cat,
                    rule_name=rule,
                    severity=severity,
                    detail=detail,
                    risk_score=random.randint(70, 99),
                    mitigation=mitigation,
                    ts=event_time
                )
                db.session.add(signal)

            # Create Event (for Live Events page)
            # Map alert severity/category to Event fields
            event_type = "alert"
            if "Malware" in title or "C2" in title: event_type = "threat"
            
            event = Event(
                organization_id=org_id,
                device_id=device.id,
                event_type=event_type,
                category=category,
                severity=severity,
                message=detail,
                mitigation=mitigation if "ai_signal" in scenario else None,
                ts=event_time
            )
            db.session.add(event)

        db.session.commit()
        print("--- Simulation Complete ---")
        print("Check the Dashboard for new alerts and AI insights.")

if __name__ == "__main__":
    simulate_attacks()
