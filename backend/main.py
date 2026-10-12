from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.privacy_guard import redact_pii

app = FastAPI(title="Secure Tax Assistant API", version="0.1.0")

# Configure CORS so your React frontend on port 5173 can talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for incoming POST requests requiring text payload
class TextPayload(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "Secure Tax Assistant Backend API Connected!"
    }

@app.get("/calculate-tax/")
def calculate_tax(income: float, rate: float = 0.15):
    """
    Calculate simple tax based on income and a tax rate.
    """
    tax_owed = income * rate
    return {
        "income": income,
        "tax_rate": rate,
        "tax_owed": tax_owed
    }

@app.post("/redact/")
def redact_text(payload: TextPayload):
    """
    Accepts raw text containing potential PII and returns the scrubbed text.
    """
    cleaned_text = redact_pii(payload.text)
    return {
        "original_received": payload.text,
        "redacted_text": cleaned_text
    }