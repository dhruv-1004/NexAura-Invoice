from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

db = SessionLocal()

# Try to find the existing admin
existing_admin = db.query(User).filter(User.email == "admin@nexaura.com").first()

if existing_admin:
    existing_admin.email = "nexauraiofficial@gmail.com"
    existing_admin.password_hash = get_password_hash("Nexaura@01")
    db.commit()
    print("Admin credentials updated successfully!")
else:
    # If the other script didn't work for some reason, create it fresh
    new_admin = db.query(User).filter(User.email == "nexauraiofficial@gmail.com").first()
    if not new_admin:
        admin = User(
            name="NexAura Admin",
            email="nexauraiofficial@gmail.com",
            password_hash=get_password_hash("Nexaura@01"),
            role=UserRole.Admin
        )
        db.add(admin)
        db.commit()
        print("New admin user created successfully with requested credentials!")
    else:
        new_admin.password_hash = get_password_hash("Nexaura@01")
        db.commit()
        print("Admin password updated successfully!")
