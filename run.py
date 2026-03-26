from app import create_app
from app.extensions import db
from app.models import User


app = create_app()
# Create admin user if not exists
with app.app_context():
    db.create_all()

    if not User.query.filter_by(email="admin@example.com").first():
        user = User(
            full_name="Admin User",
            email="admin@example.com",
            role="Admin"
        )
        user.set_password("Admin123!")
        db.session.add(user)
        db.session.commit()
        print("✅ Admin user created")
    else:
        print("ℹ️ Admin already exists")
