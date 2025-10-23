# app/__init__.py
import os
from flask import Flask
from .extensions import db, migrate, login_manager, bcrypt, mail, cors
from config import Config


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # -------------------------
    # Load config and instance folder
    # -------------------------
    app.config.from_object(Config)
    os.makedirs(app.instance_path, exist_ok=True)

    # -------------------------
    # Initialize extensions
    # -------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    mail.init_app(app)
    cors.init_app(app)

    # -------------------------
    # Flask-Login Setup
    # -------------------------
    from app.models.user import User
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # -------------------------
    # Register Blueprints (Clean order)
    # -------------------------
    from app.routes.auth import auth as auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.api import api_bp
    from app.routes.register_flow import register_flow

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp, url_prefix="/api")  # ✅ only one instance
    app.register_blueprint(register_flow, url_prefix="/register")

    # Optional (uncomment only if needed)
    # from app.routes.onboarding import onboarding_bp
    # from app.routes.admin import admin_bp
    # from app.routes.dashboard_admin import dashboard_admin_bp
    # from app.routes.register_org import register_org_bp
    # app.register_blueprint(onboarding_bp)
    # app.register_blueprint(admin_bp)
    # app.register_blueprint(dashboard_admin_bp)
    # app.register_blueprint(register_org_bp)

    # -------------------------
    # Import models for Alembic auto-detect
    # -------------------------
    from app.models import (
        Organization,
        User,
        Subscription,
        Device,
        SecurityEvent,
        AlertPreference,
        NotificationChannel,
    )

    # -------------------------
    # Health Check Route
    # -------------------------
    @app.route("/healthz")
    def healthz():
        return {"ok": True}, 200

    return app
