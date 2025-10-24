# app/config/plans.py
PLAN_CATALOG = {
    1: {
        "id": 1,
        "slug": "basic",
        "name": "Basic",
        "price": 29,
        "max_users": 3,
        "max_devices": 5,
        "features": [
            "Basic endpoint monitoring",
            "Email alerts",
        ],
        # Feature gates
        "supports_sms": False,
        "supports_sos_voice": False,   # SOS not in Basic
        "supports_ai": False,
    },
    2: {
        "id": 2,
        "slug": "pro",
        "name": "Professional",
        "price": 79,
        "max_users": 10,
        "max_devices": 20,
        "features": [
            "Advanced reporting dashboard",
            "Custom alert rules",
            "Email & SMS alerts",
        ],
        "supports_sms": True,
        "supports_sos_voice": True,    # ✅ SOS in Pro
        "supports_ai": False,
    },
    3: {
        "id": 3,
        "slug": "enterprise",
        "name": "Enterprise",
        "price": 199,
        "max_users": None,
        "max_devices": None,
        "features": [
            "Unlimited users & devices",
            "AI-based analytics",
            "Role-based access control",
            "24/7 priority response",
        ],
        "supports_sms": True,
        "supports_sos_voice": True,    # ✅ SOS in Enterprise
        "supports_ai": True,
    },
}

def plan_for_id(plan_id: int):
    return PLAN_CATALOG.get(int(plan_id))
