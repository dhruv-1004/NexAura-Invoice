from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

db = SessionLocal()
existing_admin = db.query(User).filter(User.email == "admin@nexaura.com").first()

if not existing_admin:
    admin = User(
        name="NexAura Admin",
        email="admin@nexaura.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.Admin
    )
    db.add(admin)
    db.commit()
    print("Admin user created successfully!")
else:
    print("Admin user already exists.")
