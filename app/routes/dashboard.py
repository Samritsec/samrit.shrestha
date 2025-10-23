# app/routes/dashboard.py
from datetime import datetime, timedelta
import random
from flask import Blueprint, render_template, jsonify  # ⬅ add jsonify
from flask_login import current_user, login_required
from app.security.permissions import role_required

dashboard_bp = Blueprint("dashboard", __name__)

# ---------------------------
# Mock Data Helpers (Phase 1)
# ---------------------------
OS_CHOICES = ["Windows 11", "Windows 10", "Ubuntu 22.04", "Rocky Linux 9", "macOS 14"]
HOST_PREFIX = ["workstation", "laptop", "server", "gateway", "appliance"]

def _rand_ip():
    return f"192.168.{random.randint(0, 20)}.{random.randint(3, 250)}"

def _mock_devices(n=18):
    devices = []
    now = datetime.utcnow()
    for i in range(n):
        os = random.choice(OS_CHOICES)
        hostname = f"{random.choice(HOST_PREFIX)}-{random.randint(1, 99)}"
        status = random.choice(["online"] * 4 + ["offline"])  # ~80% online
        cpu = random.randint(3, 95)
        mem = random.randint(5, 92)
        unusual = (cpu > 85 or mem > 85) and status == "online"
        last_seen = now - timedelta(minutes=random.randint(1, 180) if status == "online" else random.randint(200, 1440))
        devices.append({
            "hostname": hostname,
            "os": os,
            "ip": _rand_ip(),
            "status": status,
            "cpu": cpu,
            "mem": mem,
            "unusual": unusual,
            "last_seen": last_seen,
        })
    return devices

def _mock_events(n=10):
    severities = ["info", "low", "medium", "high", "critical"]
    types = ["Suspicious Login", "Bruteforce Attempt", "Unregistered Device", "Malware Flag", "Data Exfiltration"]
    now = datetime.utcnow()
    events = []
    for _ in range(n):
        sev = random.choices(severities, weights=[3, 4, 5, 3, 2])[0]
        evt = random.choice(types)
        ts = now - timedelta(minutes=random.randint(1, 720))
        desc = f"{evt} detected on {_rand_ip()}."
        events.append({
            "severity": sev,
            "event_type": evt,
            "timestamp": ts,
            "description": desc
        })
    return sorted(events, key=lambda e: e["timestamp"], reverse=True)

def _aggregate(devices):
    total = len(devices)
    online = sum(1 for d in devices if d["status"] == "online")
    offline = total - online
    unusual = sum(1 for d in devices if d["unusual"])
    last_login = max((d["last_seen"] for d in devices if d["status"] == "online"), default=None)
    return {
        "total": total,
        "online": online,
        "offline": offline,
        "unusual": unusual,
        "last_login": last_login,
        "uptime_pct": round((online / total) * 100, 1) if total else 0.0
    }

def _sparkline_points(count=20, base=12, jitter=4):
    pts = []
    val = base
    for _ in range(count):
        val = max(0, val + random.randint(-jitter, jitter))
        pts.append(val)
    return pts

# ---------------------------
# Landing -> route by role
# ---------------------------
@dashboard_bp.route("/")
@login_required
def index():
    if current_user.role == "admin":
        return admin_dashboard()
    else:
        return user_dashboard()

# ---------------------------
# User Dashboard (read-only)
# ---------------------------
@dashboard_bp.route("/dashboard/user")
@login_required
def user_dashboard():
    devices = _mock_devices(10)
    events = _mock_events(8)
    agg = _aggregate(devices)
    trend_threats = _sparkline_points(base=8, jitter=3)

    return render_template(
        "dashboard_user.html",
        user=current_user,
        org=getattr(current_user, "organization", None),
        devices=devices,
        events=events,
        agg=agg,
        trend_threats=trend_threats,
    )

# ---------------------------
# Admin Dashboard (full power)
# ---------------------------
@dashboard_bp.route("/dashboard/admin")
@role_required("admin")
def admin_dashboard():
    devices = _mock_devices(22)
    events = _mock_events(12)
    agg = _aggregate(devices)

    trend_threats = _sparkline_points(base=10, jitter=5)
    trend_cpu = _sparkline_points(base=35, jitter=10)
    trend_mem = _sparkline_points(base=40, jitter=12)

    status_counts = {
        "online": agg["online"],
        "offline": agg["offline"],
        "unusual": agg["unusual"],
    }

    return render_template(
        "dashboard_admin.html",
        user=current_user,
        org=getattr(current_user, "organization", None),
        devices=devices,
        events=events,
        agg=agg,
        status_counts=status_counts,
        trend_threats=trend_threats,
        trend_cpu=trend_cpu,
        trend_mem=trend_mem,
    )

# ---------------------------
# NEW: API - Heavy load devices (mock)
# ---------------------------
@dashboard_bp.route("/api/load-heavy")
@role_required("admin")
def api_load_heavy():
    # Recompute a fresh mock set (in Phase 2 we'll read from DB)
    devices = _mock_devices(50)
    heavy = [
        d for d in devices
        if d["status"] == "online" and (d["cpu"] >= 85 or d["mem"] >= 85)
    ]
    # jsonify-friendly (serialize datetime)
    def _ser(d):
        return {
            **{k: v for k, v in d.items() if k != "last_seen"},
            "last_seen": d["last_seen"].strftime("%Y-%m-%d %H:%M UTC")
        }
    return jsonify({
        "count": len(heavy),
        "items": [_ser(d) for d in heavy]
    })
