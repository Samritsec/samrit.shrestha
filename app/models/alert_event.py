from app.extensions import db
from datetime import datetime

class AlertEvent(db.Model):
    __tablename__ = "alert_event"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organization.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    organization = db.relationship("Organization")

    def __repr__(self):
        return f"<AlertEvent {self.severity}>"
