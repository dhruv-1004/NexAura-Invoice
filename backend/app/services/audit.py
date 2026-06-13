from sqlalchemy.orm import Session
from app.models.audit import AuditLog

def log_action(db: Session, user_id, action: str, entity_type: str, entity_id):
    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id)
    )
    db.add(audit_entry)
    db.commit()
