# app/models/__init__.py
from app.extensions import db

from .organization import Organization
from .user import User
from .subscription import Subscription
from .device import Device
from .security_event import SecurityEvent
from .alerting import AlertPreference, NotificationChannel, ALERT_TYPES  # ← lives here

__all__ = [
    "db",
    "Organization",
    "User",
    "Subscription",
    "Device",
    "SecurityEvent",
    "AlertPreference",
    "NotificationChannel",
    "ALERT_TYPES",
]
