from app import create_app, db
from app.models.user import User
from app.extensions import bcrypt

app = create_app()
with app.app_context():
    user = User.query.filter_by(username="admin").first()
    if user:
        # Use the model's method which uses bcrypt
        user.set_password("admin")
        db.session.commit()
        print("Admin password reset to 'admin' using bcrypt")
    else:
        print("Admin user not found")
