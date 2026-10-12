"""
main.py
Secure Tax Assistant — FastAPI Backend

Endpoints:
    GET  /                          — Health check
    POST /redact/                   — PII scrubbing with audit trail
    GET  /organizer/{client_id}     — Multi-Year Tax Organizer (Ollama + RAG)
    POST /upload-document/          — Simulated document ingestion
    POST /trigger-lookup/           — Sales assistant trigger-phrase routing
    GET  /client/{client_id}/status — Checklist progress for frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

from backend.privacy_guard import redact_pii, redact_pii_with_audit
from backend.rag_organizer import generate_tax_organizer
from backend.database import DB_PATH

app = FastAPI(title="Secure Tax Assistant API", version="1.0")

# ─── CORS ────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Schemas ─────────────────────────────────────────────────────────────────────

class TextPayload(BaseModel):
    text: str


class DocumentUploadPayload(BaseModel):
    client_id: int
    tax_year: int
    document_name: str
    simulated_text: str


class TriggerPayload(BaseModel):
    client_id: int
    phrase: str


# ─── Endpoints ───────────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"message": "Secure Tax Assistant Backend is running!"}


@app.post("/redact/")
def redact_endpoint(payload: TextPayload):
    """Scrub sensitive PII from incoming text using the privacy guard."""
    result = redact_pii_with_audit(payload.text)
    return {
        "original": payload.text,
        "redacted": result.redacted_text,
        "findings_count": result.count,
        "findings": result.findings,
    }


@app.get("/organizer/{client_id}")
def get_tax_organizer(client_id: int):
    """
    Fetch client data, run it through local Ollama via RAG,
    and return a structured Multi-Year Tax Organizer in markdown.
    """
    try:
        organizer_md = generate_tax_organizer(client_id)
        if organizer_md == "Client not found":
            raise HTTPException(status_code=404, detail="Client not found")
        return {"client_id": client_id, "organizer": organizer_md}
    except HTTPException:
        raise
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

    cleaned_preview = redact_pii(payload.simulated_text)[:100] + "..."

    return {
        "message": f"Successfully ingested {payload.document_name} for Tax Year {payload.tax_year}!",
        "client_id": payload.client_id,
        "status": "Received",
        "extracted_preview": cleaned_preview,
    }


@app.post("/trigger-lookup/")
def trigger_lookup(payload: TriggerPayload):
    """
    Matches a trigger phrase against the client's checklist and
    returns recommended next steps for the sales assistant.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tax_year, document_name FROM checklists
        WHERE client_id = ? AND status = 'Missing'
    """, (payload.client_id,))
    missing = cursor.fetchall()
    conn.close()

    recommendations = []
    phrase_lower = payload.phrase.lower()

    if "audit" in phrase_lower:
        recommendations.append("Pull prior-year return and confirm filing status.")
        recommendations.append("Check for CP2000 / CP2100 notice type.")
        recommendations.append("Escalate to senior preparer if balance > $5,000.")
    elif "w-2" in phrase_lower:
        w2_missing = [f"{y}" for y, d in missing if "w-2" in d.lower()]
        recommendations.append(f"Outstanding W-2s: {w2_missing if w2_missing else 'None tracked'}")
        recommendations.append("Offer client the e-verify W-2 request option.")
    elif "1099" in phrase_lower:
        form_1099_missing = [f"{y}" for y, d in missing if "1099" in d.lower()]
        recommendations.append(f"Outstanding 1099s: {form_1099_missing if form_1099_missing else 'None tracked'}")
        recommendations.append("Send client the 1099 substitution letter template.")
    else:
        recommendations.append("No specific trigger matched. Review transcript manually.")

    return {
        "client_id": payload.client_id,
        "phrase": payload.phrase,
        "missing_documents": [f"{y} — {d}" for y, d in missing],
        "recommendations": recommendations,
    }


@app.get("/client/{client_id}/status")
def client_status(client_id: int):
    """Return the client's document checklist progress (for the frontend progress bar)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT document_name, tax_year, status FROM checklists
        WHERE client_id = ?
    """, (client_id,))
    rows = cursor.fetchall()
    conn.close()

    total = len(rows)
    received = sum(1 for r in rows if r[2] == "Received")

    return {
        "client_id": client_id,
        "progress": f"{received}/{total}",
        "percent": int((received / total) * 100) if total else 0,
        "checklist": [
            {"doc": r[0], "year": r[1], "status": r[2]} for r in rows
        ],
    }   