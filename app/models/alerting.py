from app.extensions import db

# Keep this set in one place so routes can import it safely
ALERT_TYPES = {
    "bruteforce",
    "unregistered_device",
    "malware",
    "data_exfil",
    "suspicious_login",
}

class AlertPreference(db.Model):
    __tablename__ = "alert_preference"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organization.id"), nullable=False)

    # Store list of enabled alert types; PickleType works across SQLite quickly
    enabled_types = db.Column(db.PickleType, default=list)

    # “SOS” toggle for voice calls on critical events
    voice_call_on_critical = db.Column(db.Boolean, default=False)

    organization = db.relationship("Organization", back_populates="alert_pref")

class NotificationChannel(db.Model):
    __tablename__ = "notification_channel"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organization.id"), nullable=False)

    # e.g. "email", "sms", "voice", "webhook"
    kind = db.Column(db.String(20), nullable=False)
    value = db.Column(db.String(120), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)

    organization = db.relationship("Organization", back_populates="channels")
