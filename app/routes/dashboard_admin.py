# --- Organization Admin Dashboard ---
@dashboard_bp.route("/dashboard/admin")
@login_required
def org_admin_dashboard():
    org = current_user.organization

    # 🧪 Mocked Security Events (will be replaced later with real data)
    events = [
        {"severity": "critical", "event_type": "Ransomware Detected", "timestamp": "2025-10-16 02:40:12", "description": "Malware found on Workstation-03"},
        {"severity": "high", "event_type": "Unauthorized Access", "timestamp": "2025-10-15 22:11:45", "description": "Suspicious login from new device"},
        {"severity": "medium", "event_type": "Firewall Port Scan", "timestamp": "2025-10-15 19:25:09", "description": "Multiple connection attempts from unknown IP"},
    ]

    # 🧪 Mocked Users and Devices
    users = [
        {"username": "admin", "email": "admin@tenshiguard.com", "role": "Admin", "status": "Active"},
        {"username": "it_support", "email": "support@tenshiguard.com", "role": "User", "status": "Active"},
        {"username": "intern", "email": "intern@tenshiguard.com", "role": "User", "status": "Suspended"},
    ]

    devices = [
        {"hostname": "Server-01", "os": "Ubuntu 22.04", "ip": "192.168.0.10", "status": "online"},
        {"hostname": "Workstation-03", "os": "Windows 11", "ip": "192.168.0.33", "status": "offline"},
        {"hostname": "Laptop-02", "os": "macOS 14", "ip": "192.168.0.25", "status": "online"},
    ]

    metrics = {
        "active_users": 2,
        "devices_online": 2,
        "critical_alerts": 1,
        "compliance_score": 88,
    }

    return render_template(
        "dashboard_admin.html",
        org=org,
        users=users,
        devices=devices,
        events=events,
        metrics=metrics
    )
