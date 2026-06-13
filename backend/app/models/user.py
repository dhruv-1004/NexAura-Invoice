import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Enum, DateTime, Uuid
from app.db.database import Base
import enum

class UserRole(str, enum.Enum):
    Admin = "Admin"
    Staff = "Staff"

class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.Staff, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
