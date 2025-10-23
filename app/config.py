import os

# =========================================================
# 📦 Base Directory Setup
# =========================================================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # =========================================================
    # 🔹 Core Application Settings
    # =========================================================
    SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey-change-this")

    # Database URI (SQLite for dev, can be PostgreSQL/MySQL later)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "tenshiguard.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =========================================================
    # 🔹 Mail Configuration (Flask-Mail)
    # Used for password reset, alerts, notifications
    # =========================================================
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "8025"))  # Debug SMTP port
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "False").lower() in ("true", "1")
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "False").lower() in ("true", "1")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER",
        "TenshiGuard <noreply@tenshiguard.local>"
    )

    # =========================================================
    # 🔹 Security Tokens (for password reset, MFA, etc.)
    # =========================================================
    SECURITY_TOKEN_EXPIRATION = int(os.environ.get("SECURITY_TOKEN_EXPIRATION", 3600))  # 1 hour

    # MFA optional toggle
    MFA_ENABLED = os.environ.get("MFA_ENABLED", "True").lower() in ("true", "1")

    # =========================================================
    # 🔹 Alert Integrations (Twilio, optional)
    # =========================================================
    # These are safe to leave blank — system will auto-disable calls if unset
    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER", "")

    # =========================================================
    # 🔹 Billing / Payment (for future upgrade)
    # =========================================================
    STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    # =========================================================
    # 🔹 Wazuh Integration (future use)
    # =========================================================
    WAZUH_API_URL = os.environ.get("WAZUH_API_URL", "https://localhost:55000")
    WAZUH_API_USER = os.environ.get("WAZUH_API_USER", "wazuh")
    WAZUH_API_PASS = os.environ.get("WAZUH_API_PASS", "wazuh")

    # =========================================================
    # 🔹 Flask App Configuration
    # =========================================================
    # Enable debugging features (for development)
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")

    # Limit file uploads (for future log imports)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Enable CORS for frontend integration
    CORS_HEADERS = "Content-Type"

    # =========================================================
    # 🔹 Paths & Instance Management
    # =========================================================
    INSTANCE_FOLDER_PATH = os.path.join(BASE_DIR, "instance")
    if not os.path.exists(INSTANCE_FOLDER_PATH):
        os.makedirs(INSTANCE_FOLDER_PATH, exist_ok=True)
