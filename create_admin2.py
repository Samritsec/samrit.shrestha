from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    if not User.query.filter_by(username="admin2").first():
        user = User(username="admin2", email="admin2@test.com", role="admin")
        user.set_password("admin")
        db.session.add(user)
        db.session.commit()
        print("Created admin2")
    else:
        print("admin2 exists")
