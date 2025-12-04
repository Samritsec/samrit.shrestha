from app import create_app
from app.models.user import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username="admin").first()
    if user:
        print(f"Admin Email: {user.email}")
    else:
        print("Admin user not found")
