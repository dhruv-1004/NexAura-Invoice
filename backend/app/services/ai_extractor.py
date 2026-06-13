import json
import io
from pypdf import PdfReader
from google import genai
from google.genai import types
from app.core.config import settings

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def parse_invoice_with_gemini(raw_text: str) -> dict:
    if not settings.GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY is not set.")
    
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    prompt = """
    You are an expert invoice data extractor. Extract the following information from the provided invoice text.
    Return ONLY a valid JSON object matching this schema, without any markdown formatting like ```json.
    
    {
      "client_name": "String",
      "client_address": "String",
      "invoice_number": "String",
      "issue_date": "YYYY-MM-DD",
      "due_date": "YYYY-MM-DD",
      "subtotal": Number,
      "discount": Number,
      "grand_total": Number,
      "items": [
        {
          "service_name": "String",
          "description": "String",
          "amount": Number
        }
      ]
    }
    
    Invoice Text:
    """ + raw_text

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    
    return json.loads(response.text)
