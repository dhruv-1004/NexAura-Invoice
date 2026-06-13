from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.invoice import Invoice

def generate_invoice_number(db: Session) -> str:
    current_year = datetime.now().year
    
    # Find the latest invoice number for the current year
    # Format: NXA-YYYY/XXX
    prefix = f"NXA-{current_year}/"
    
    latest_invoice = (
        db.query(Invoice)
        .filter(Invoice.invoice_number.like(f"{prefix}%"))
        .order_by(Invoice.invoice_number.desc())
        .first()
    )
    
    if latest_invoice:
        # Extract the sequence number
        last_seq_str = latest_invoice.invoice_number.split('/')[-1]
        try:
            next_seq = int(last_seq_str) + 1
        except ValueError:
            next_seq = 1
    else:
        next_seq = 1
        
    return f"{prefix}{next_seq:03d}"
