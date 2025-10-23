from datetime import datetime
from app.extensions import db

class Organization(db.Model):
    __tablename__ = "organization"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    sector = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Counters / status
    total_users = db.Column(db.Integer, default=0)
    total_devices = db.Column(db.Integer, default=0)
    is_paid = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(50), default="lead")

    # Subscription
    subscription_id = db.Column(db.Integer, db.ForeignKey("subscription.id"))

    # Relationships (use paired back_populates to avoid name collisions)
    users   = db.relationship("User", back_populates="organization", lazy=True)
    devices = db.relationship("Device", back_populates="organization", lazy=True)
    alerts  = db.relationship("SecurityEvent", back_populates="organization", lazy=True)

    # (Optional) if you want explicit relations for alert prefs / channels:
    alert_pref = db.relationship("AlertPreference", back_populates="organization", uselist=False, lazy=True)
    channels   = db.relationship("NotificationChannel", back_populates="organization", lazy=True)

    def __repr__(self):
        return f"<Organization {self.name}>"
