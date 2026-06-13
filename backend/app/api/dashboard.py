from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from typing import Any
from app.db.database import get_db
from app.models.invoice import Invoice, InvoiceStatus
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    now = datetime.now(timezone.utc)
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first_day_of_week = now - timedelta(days=now.weekday())
    first_day_of_week = first_day_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    # Monthly Revenue
    monthly_revenue = db.query(func.sum(Invoice.grand_total)).filter(
        Invoice.issue_date >= first_day_of_month,
        Invoice.status != InvoiceStatus.Cancelled
    ).scalar() or 0.0

    # Weekly Revenue
    weekly_revenue = db.query(func.sum(Invoice.grand_total)).filter(
        Invoice.issue_date >= first_day_of_week,
        Invoice.status != InvoiceStatus.Cancelled
    ).scalar() or 0.0

    # Counts
    total_invoices = db.query(func.count(Invoice.id)).filter(Invoice.status != InvoiceStatus.Archived).scalar() or 0
    paid_invoices = db.query(func.count(Invoice.id)).filter(Invoice.status == InvoiceStatus.Paid).scalar() or 0
    pending_invoices = db.query(func.count(Invoice.id)).filter(Invoice.status.in_([InvoiceStatus.Draft, InvoiceStatus.Sent])).scalar() or 0
    cancelled_invoices = db.query(func.count(Invoice.id)).filter(Invoice.status == InvoiceStatus.Cancelled).scalar() or 0

    # Top Clients (by total revenue)
    top_clients_query = (
        db.query(Invoice.client_name, func.sum(Invoice.grand_total).label("total_revenue"))
        .filter(Invoice.status != InvoiceStatus.Cancelled)
        .group_by(Invoice.client_name)
        .order_by(func.sum(Invoice.grand_total).desc())
        .limit(5)
        .all()
    )
    top_clients = [{"client_name": client, "revenue": float(rev)} for client, rev in top_clients_query]

    return {
        "monthly_revenue": float(monthly_revenue),
        "weekly_revenue": float(weekly_revenue),
        "total_invoices": total_invoices,
        "paid_invoices": paid_invoices,
        "pending_invoices": pending_invoices,
        "cancelled_invoices": cancelled_invoices,
        "top_clients": top_clients
    }
