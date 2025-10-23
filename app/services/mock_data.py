# app/services/mock_data.py
from datetime import datetime, timedelta
import random

SEVERITIES = ["info", "low", "medium", "high", "critical"]

def mock_org_summary():
    return {
        "name": "TenshiGuard Academy",
        "sector": "Academic",
        "plan_name": "Enterprise",
        "max_users": 50,
        "max_devices": 200,
        "total_users": 8,
        "total_devices": 14,
        "is_paid": True,
        "status": "active",
    }

def mock_user_list(count=6):
    base = [
        {"username":"admin", "email":"admin@tenshiguard.com", "role":"admin"},
        {"username":"user01","email":"user01@tenshiguard.com","role":"user"},
        {"username":"user02","email":"user02@tenshiguard.com","role":"user"},
        {"username":"analyst","email":"analyst@tenshiguard.com","role":"user"},
        {"username":"ops","email":"ops@tenshiguard.com","role":"user"},
        {"username":"lead","email":"lead@tenshiguard.com","role":"user"},
    ]
    return base[:count]

def mock_device_list(count=8):
    os_list = ["Windows 11", "Ubuntu 22.04", "macOS 14", "Rocky Linux 9", "Windows Server 2022"]
    devices = []
    for i in range(count):
        devices.append({
            "hostname": f"Host-{i+1:02d}",
            "ip": f"192.168.0.{100+i}",
            "os": random.choice(os_list),
            "status": random.choice(["online","online","online","offline"]),  # mostly online
        })
    return devices

def mock_event_list(limit=10):
    types = [
        "Suspicious login",
        "Malware signature detected",
        "Firewall rule change",
        "Multiple failed logins",
        "Privileged escalation attempt",
        "Policy non-compliance",
        "Anomalous outbound traffic",
        "Ransomware pattern detected",
        "USB device inserted",
        "WMI persistence detected",
    ]
    out = []
    now = datetime.utcnow()
    for i in range(limit):
        out.append({
            "event_type": random.choice(types),
            "severity": random.choice(SEVERITIES),
            "description": "Automated detection event (demo)",
            "timestamp": now - timedelta(minutes=5*i + random.randint(1,4))
        })
    return out
