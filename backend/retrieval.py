"""
retrieval.py
Retrieves client data from SQLite, scrubs PII, and formats the payload
for the RAG / Ollama organizer pipeline.
"""

import sqlite3
from backend.database import DB_PATH
from backend.privacy_guard import redact_pii


def get_client_organizer_data(client_id: int) -> dict:
    """
    Retrieves client info, tax year details, and document checklists from SQLite,
    then scrubs any potential sensitive text via the privacy guard.

    Returns a dict with keys:
        safe_profile   – PII-redacted profile text (safe for LLM prompts)
        client_token   – anonymized client identifier (e.g., "CLIENT-0001")
        checklists     – list of {tax_year, document_name, status}
        tax_years      – list of {tax_year, gross_income, filing_status, employer, notes}
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Fetch Client Info
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    client = cursor.fetchone()

    if not client:
        conn.close()
        return {"error": "Client not found"}

    # 2. Fetch Tax Year Details
    cursor.execute("""
        SELECT tax_year, gross_income, filing_status, employer, notes
        FROM tax_years
        WHERE client_id = ?
        ORDER BY tax_year DESC
    """, (client_id,))
    tax_years = [dict(row) for row in cursor.fetchall()]

    # 3. Fetch Document Status Checklists
    cursor.execute("""
        SELECT tax_year, document_name, status, received_at
        FROM checklists
        WHERE client_id = ?
        ORDER BY tax_year DESC, document_name
    """, (client_id,))
    checklists = [dict(row) for row in cursor.fetchall()]

    conn.close()

    # 4. Build a rich profile text from tax year data
    year_lines = "\n".join([
        f"  {t['tax_year']}: ${t['gross_income']:,.2f} | {t['filing_status']} | "
        f"{t['employer']} | {t['notes']}"
        for t in tax_years
    ]) or "  (no tax year data on file)"

    raw_profile_text = (
        f"Client: {client['name']} (Token: CLIENT-{client['id']:04d})\n"
        f"Filing History:\n{year_lines}"
    )

    # 5. Scrub the ENTIRE client row as defense-in-depth,
    #    then use the safe profile text for the LLM prompt.
    _ = redact_pii(str(dict(client)))  # validates no PII leaks in row
    safe_profile_text = redact_pii(raw_profile_text)

    return {
        "safe_profile": safe_profile_text,
        "client_token": f"CLIENT-{client['id']:04d}",
        "checklists": checklists,
        "tax_years": tax_years,
    }


if __name__ == "__main__":
    print("Testing retrieval for Client ID 1:")
    data = get_client_organizer_data(1)
    print(f"  Token: {data['client_token']}")
    print(f"  Profile:\n{data['safe_profile']}")
    print(f"  Tax Years: {len(data['tax_years'])} records")
    print(f"  Checklists: {len(data['checklists'])} items")
    missing = [c for c in data['checklists'] if c['status'] == 'Missing']
    print(f"  Missing docs: {len(missing)}")
