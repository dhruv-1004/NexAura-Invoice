from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import Any
from app.db.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.services.ai_extractor import extract_text_from_pdf, parse_invoice_with_gemini

router = APIRouter()

@router.post("/extract-invoice")
async def extract_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        contents = await file.read()
        raw_text = extract_text_from_pdf(contents)
        if not raw_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")
            
        parsed_data = parse_invoice_with_gemini(raw_text)
        return parsed_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process invoice: {str(e)}")
