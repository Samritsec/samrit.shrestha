from datetime import datetime
from app.extensions import db

class SecurityEvent(db.Model):
    __tablename__ = "security_event"

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(120))
    description = db.Column(db.Text)
    severity = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # REQUIRED FKs so relationships can join properly
    organization_id = db.Column(db.Integer, db.ForeignKey("organization.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    # Relationships (paired with Organization.alerts and User.events)
    organization = db.relationship("Organization", back_populates="alerts")
    user = db.relationship("User", back_populates="events")

    def __repr__(self):
        return f"<SecurityEvent {self.event_type}>"
