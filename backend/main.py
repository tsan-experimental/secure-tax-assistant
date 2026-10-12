from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from backend.privacy_guard import redact_pii
from backend.rag_organizer import generate_tax_organizer
from backend.database import DB_PATH

app = FastAPI(title="Secure Tax Assistant API", version="1.0")

# Allow requests from Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextPayload(BaseModel):
    text: str

class DocumentUploadPayload(BaseModel):
    client_id: int
    tax_year: int
    document_name: str
    simulated_text: str

@app.get("/")
def read_root():
    return {"message": "Secure Tax Assistant Backend is running!"}

@app.post("/redact/")
def redact_endpoint(payload: TextPayload):
    """
    Endpoint to scrub sensitive PII from incoming text using our privacy guard.
    """
    cleaned_text = redact_pii(payload.text)
    return {"original": payload.text, "redacted": cleaned_text}

@app.get("/organizer/{client_id}")
def get_tax_organizer(client_id: int):
    """
    Endpoint to fetch client data securely, run it through local Ollama,
    and return a structured Multi-Year Tax Organizer markdown report.
    """
    try:
        organizer_md = generate_tax_organizer(client_id)
        if organizer_md == "Client not found":
            raise HTTPException(status_code=404, detail="Client not found")
        return {"client_id": client_id, "organizer": organizer_md}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-document/")
def upload_document(payload: DocumentUploadPayload):
    """
    Simulates uploading a missing tax document, parsing its contents, 
    and updating the client's checklist status from Missing to Received.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if the document entry exists for this client and tax year
    cursor.execute("""
        SELECT id, status FROM checklists 
        WHERE client_id = ? AND tax_year = ? AND document_name = ?
    """, (payload.client_id, payload.tax_year, payload.document_name))
    
    row = cursor.fetchone()

    if not row:
        cursor.execute("""
            INSERT INTO checklists (client_id, tax_year, document_name, status)
            VALUES (?, ?, ?, 'Received')
        """, (payload.client_id, payload.tax_year, payload.document_name))
    else:
        cursor.execute("""
            UPDATE checklists SET status = 'Received'
            WHERE client_id = ? AND tax_year = ? AND document_name = ?
        """, (payload.client_id, payload.tax_year, payload.document_name))

    conn.commit()
    conn.close()

    return {
        "message": f"Successfully ingested {payload.document_name} for Tax Year {payload.tax_year}!",
        "client_id": payload.client_id,
        "status": "Received",
        "extracted_preview": payload.simulated_text[:100] + "..."
    }