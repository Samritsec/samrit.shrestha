from datetime import datetime
from app.extensions import db

class Device(db.Model):
    __tablename__ = "device"

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(120), nullable=False)
    ip_address = db.Column(db.String(45))
    os = db.Column(db.String(80))
    status = db.Column(db.String(50), default="active")
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    organization_id = db.Column(db.Integer, db.ForeignKey("organization.id"))
    organization = db.relationship("Organization", back_populates="devices")

    def __repr__(self):
        return f"<Device {self.hostname}>"
