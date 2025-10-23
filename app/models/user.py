from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt

class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="user")
    sector = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Org / subscription links
    organization_id = db.Column(db.Integer, db.ForeignKey("organization.id"))
    subscription_id = db.Column(db.Integer, db.ForeignKey("subscription.id"), nullable=True)

    # Relationships
    organization = db.relationship("Organization", back_populates="users")
    events = db.relationship("SecurityEvent", back_populates="user", lazy=True)

    # Password helpers
    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"
