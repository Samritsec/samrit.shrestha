from app import create_app, db
import logging
import os

# =========================================================
# 🔹 Create Flask App
# =========================================================
app = create_app()

# =========================================================
# 🔹 Logging Setup
# =========================================================
if not os.path.exists("logs"):
    os.mkdir("logs")

logging.basicConfig(
    filename="logs/tenshiguard.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.getLogger().addHandler(logging.StreamHandler())

logging.info("🚀 TenshiGuard server starting...")

# =========================================================
# 🔹 Run Application
# =========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
