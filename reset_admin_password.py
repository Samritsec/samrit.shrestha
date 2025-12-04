from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    user = User.query.filter_by(username="admin").first()
    if user:
        user.password_hash = generate_password_hash("admin")
        db.session.commit()
        print("Admin password reset to 'admin'")
    else:
        print("Admin user not found")
