import io
import csv
import pandas as pd
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Any
from app.db.database import get_db
from app.models.invoice import Invoice
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/monthly")
def export_monthly_report(
    format: str = 'csv', # 'csv' or 'excel'
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    now = datetime.now(timezone.utc)
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    invoices = db.query(Invoice).filter(Invoice.issue_date >= first_day_of_month).all()
    
    data = []
    for inv in invoices:
        data.append({
            "Invoice Number": inv.invoice_number,
            "Issue Date": inv.issue_date.strftime("%Y-%m-%d"),
            "Client Name": inv.client_name,
            "Subtotal": float(inv.subtotal),
            "Discount": float(inv.discount),
            "Grand Total": float(inv.grand_total),
            "Status": inv.status.value
        })
        
    df = pd.DataFrame(data)
    
    if format == 'excel':
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Monthly Report')
        buffer.seek(0)
        return StreamingResponse(
            buffer, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            headers={"Content-Disposition": "attachment; filename=monthly_report.xlsx"}
        )
    else:
        # Default to CSV
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]), 
            media_type="text/csv", 
            headers={"Content-Disposition": "attachment; filename=monthly_report.csv"}
        )
