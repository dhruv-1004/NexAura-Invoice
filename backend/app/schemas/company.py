from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional

class CompanySettingsBase(BaseModel):
    company_name: str
    address: str
    email: EmailStr
    phone: str
    logo_path: Optional[str] = None
    bank_name: str
    account_holder: str
    account_number: str
    ifsc: str
    upi_id: str
    footer_note: Optional[str] = None

class CompanySettingsCreate(CompanySettingsBase):
    pass

class CompanySettingsUpdate(CompanySettingsBase):
    pass

class CompanySettingsResponse(CompanySettingsBase):
    id: UUID

    class Config:
        from_attributes = True
