import uuid
from sqlalchemy import Column, String, Text, Uuid
from app.db.database import Base

class CompanySettings(Base):
    __tablename__ = "company_settings"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    company_name = Column(String, nullable=False)
    address = Column(Text, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    logo_path = Column(String, nullable=True)
    bank_name = Column(String, nullable=False)
    account_holder = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    ifsc = Column(String, nullable=False)
    upi_id = Column(String, nullable=False)
    footer_note = Column(Text, nullable=True)
