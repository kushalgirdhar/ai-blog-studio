from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models.user import User


app = create_app()

with app.app_context():
    user = User(
        username="admin",
        email="admin@example.com",
        password_hash=generate_password_hash("Admin@12345")
    )

    db.session.add(user)
    db.session.commit()

    print("User created successfully!")