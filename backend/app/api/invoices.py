from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from fastapi.responses import StreamingResponse
from app.db.database import get_db
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus
from app.models.company import CompanySettings
from app.models.user import User
from app.schemas.invoice import InvoiceCreate, InvoiceResponse, InvoiceUpdate
from app.api.deps import get_current_user
from app.services.invoice_generator import generate_invoice_number
from app.services.pdf_generator import generate_invoice_pdf
from app.services.audit import log_action

router = APIRouter()

@router.post("/", response_model=InvoiceResponse)
def create_invoice(
    invoice_in: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    invoice_number = generate_invoice_number(db)
    
    db_invoice = Invoice(
        invoice_number=invoice_number,
        issue_date=invoice_in.issue_date,
        due_date=invoice_in.due_date,
        client_name=invoice_in.client_name,
        billing_address=invoice_in.billing_address,
        shipping_address=invoice_in.shipping_address,
        client_tax_number=invoice_in.client_tax_number,
        subtotal=invoice_in.subtotal,
        discount=invoice_in.discount,
        grand_total=invoice_in.grand_total,
        status=invoice_in.status,
        created_by=current_user.id
    )
    db.add(db_invoice)
    db.flush() # flush to get db_invoice.id
    
    for item_in in invoice_in.items:
        db_item = InvoiceItem(
            invoice_id=db_invoice.id,
            service_name=item_in.service_name,
            description=item_in.description,
            amount=item_in.amount
        )
        db.add(db_item)
        
    db.commit()
    db.refresh(db_invoice)
    
    log_action(db, current_user.id, "Invoice Creation", "Invoice", str(db_invoice.id))
    
    return db_invoice

@router.get("/", response_model=List[InvoiceResponse])
def get_invoices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    invoices = db.query(Invoice).offset(skip).limit(limit).all()
    return invoices

@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.patch("/{invoice_id}/archive", response_model=InvoiceResponse)
def archive_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    invoice.status = InvoiceStatus.Archived
    db.commit()
    db.refresh(invoice)
    
    log_action(db, current_user.id, "Invoice Archive", "Invoice", str(invoice.id))
    
    return invoice

@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    company = db.query(CompanySettings).first()
    
    pdf_buffer = generate_invoice_pdf(invoice, company)
    
    log_action(db, current_user.id, "Invoice Download", "Invoice", str(invoice.id))
    
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename={invoice.invoice_number}.pdf"}
    )
