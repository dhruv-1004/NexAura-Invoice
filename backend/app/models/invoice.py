import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Enum, DateTime, ForeignKey, Text, Numeric, Uuid
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum

class InvoiceStatus(str, enum.Enum):
    Draft = "Draft"
    Sent = "Sent"
    Paid = "Paid"
    Cancelled = "Cancelled"
    Archived = "Archived"

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    invoice_number = Column(String, unique=True, index=True, nullable=False)
    issue_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    
    client_name = Column(String, nullable=False)
    billing_address = Column(Text, nullable=False)
    shipping_address = Column(Text, nullable=False)
    client_tax_number = Column(String, nullable=True)
    
    subtotal = Column(Numeric(10, 2), nullable=False, default=0.0)
    discount = Column(Numeric(10, 2), nullable=False, default=0.0)
    grand_total = Column(Numeric(10, 2), nullable=False, default=0.0)
    
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.Draft, nullable=False)
    
    created_by = Column(Uuid, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    invoice_id = Column(Uuid, ForeignKey("invoices.id"), nullable=False)
    service_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)

    invoice = relationship("Invoice", back_populates="items")
