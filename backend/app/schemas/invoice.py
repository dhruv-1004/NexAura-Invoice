from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from app.models.invoice import InvoiceStatus

class InvoiceItemBase(BaseModel):
    service_name: str
    description: Optional[str] = None
    amount: Decimal

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItemResponse(InvoiceItemBase):
    id: UUID
    invoice_id: UUID

    class Config:
        from_attributes = True

class InvoiceBase(BaseModel):
    issue_date: datetime
    due_date: datetime
    client_name: str
    billing_address: str
    shipping_address: str
    client_tax_number: Optional[str] = None
    subtotal: Decimal
    discount: Decimal = Decimal('0.0')
    grand_total: Decimal
    status: InvoiceStatus = InvoiceStatus.Draft

class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]

class InvoiceUpdate(BaseModel):
    issue_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    client_name: Optional[str] = None
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    client_tax_number: Optional[str] = None
    subtotal: Optional[Decimal] = None
    discount: Optional[Decimal] = None
    grand_total: Optional[Decimal] = None
    status: Optional[InvoiceStatus] = None
    items: Optional[List[InvoiceItemCreate]] = None

class InvoiceResponse(InvoiceBase):
    id: UUID
    invoice_number: str
    created_by: UUID
    created_at: datetime
    items: List[InvoiceItemResponse]

    class Config:
        from_attributes = True
