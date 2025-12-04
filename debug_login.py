from app import create_app, db
from app.models.user import User
from app.extensions import bcrypt

app = create_app()
with app.app_context():
    user = User.query.filter_by(username="admin").first()
    if user:
        print(f"User found: {user.username}")
        print(f"Role: {user.role}")
        print(f"Enabled: {user.is_enabled}")
        print(f"Password Hash: {user.password_hash}")
        
        is_valid = user.check_password("admin")
        print(f"Password 'admin' valid: {is_valid}")
        
        # Also try manual check
        manual_check = bcrypt.check_password_hash(user.password_hash, "admin")
        print(f"Manual bcrypt check: {manual_check}")
    else:
        print("User 'admin' not found")
