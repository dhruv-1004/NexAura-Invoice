from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.company import CompanySettings
from app.models.user import User
from app.schemas.company import CompanySettingsCreate, CompanySettingsUpdate, CompanySettingsResponse
from app.api.deps import get_current_user
from app.services.audit import log_action
from typing import Any

router = APIRouter()

@router.get("/", response_model=CompanySettingsResponse)
def get_company_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    settings = db.query(CompanySettings).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Company settings not configured")
    return settings

@router.put("/", response_model=CompanySettingsResponse)
def update_company_settings(
    settings_in: CompanySettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    settings = db.query(CompanySettings).first()
    if not settings:
        settings = CompanySettings(**settings_in.model_dump())
        db.add(settings)
    else:
        for var, value in vars(settings_in).items():
            setattr(settings, var, value) if value is not None else None
            
    db.commit()
    db.refresh(settings)
    
    log_action(db, current_user.id, "Settings Changes", "CompanySettings", str(settings.id))
    
    return settings
