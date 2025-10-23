import os

# Get base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # =========================================================
    # 🔐 Core Security
    # =========================================================
    SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey-change-this")

    # =========================================================
    # 🗄️ Database Configuration
    # =========================================================
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "tenshiguard.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =========================================================
    # 📧 Mail Configuration (Dual Mode)
    # =========================================================
    # Detect if we’re running locally or in production
    ENV = os.environ.get("FLASK_ENV", "development")

    if ENV == "development":
        # Local mode: use fake SMTP (aiosmtpd)
        MAIL_SERVER = "localhost"
        MAIL_PORT = 8025
        MAIL_USE_TLS = False
        MAIL_USE_SSL = False
        MAIL_USERNAME = None
        MAIL_PASSWORD = None
        MAIL_DEFAULT_SENDER = "TenshiGuard <no-reply@tenshiguard.local>"
    else:
        # Production mode: use Gmail or real SMTP service
        MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
        MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
        MAIL_USE_TLS = True
        MAIL_USE_SSL = False
        MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "your_email@gmail.com")
        MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "your_app_specific_password")
        MAIL_DEFAULT_SENDER = os.environ.get(
            "MAIL_DEFAULT_SENDER",
            "TenshiGuard <your_email@gmail.com>"
        )

    # =========================================================
    # 🕒 Token & Security Settings
    # =========================================================
    SECURITY_TOKEN_EXPIRATION = int(os.environ.get("SECURITY_TOKEN_EXPIRATION", 3600))  # 1 hour validity
    MFA_ENABLED = os.environ.get("MFA_ENABLED", "True").lower() in ["true", "1"]

    # =========================================================
    # ⚙️ Wazuh Integration (future)
    # =========================================================
    WAZUH_API_URL = os.environ.get("WAZUH_API_URL", "https://localhost:55000")
    WAZUH_API_USER = os.environ.get("WAZUH_API_USER", "wazuh")
    WAZUH_API_PASS = os.environ.get("WAZUH_API_PASS", "wazuh")

    # =========================================================
    # 🌐 Application Meta
    # =========================================================
    APP_NAME = "TenshiGuard Endpoint Security Platform"
    COMPANY_SUPPORT_EMAIL = "support@tenshiguard.com"
