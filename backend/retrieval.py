import sqlite3
from backend.privacy_guard import redact_pii

DB_PATH = "data/tax_clients.db"

def get_client_organizer_data(client_id: int):
    """
    Retrieves client info and document checklists from SQLite,
    then scrubs any potential sensitive text via the privacy guard.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows column access by name
    cursor = conn.cursor()

    # 1. Fetch Client Info
    cursor.execute("SELECT * FROM clients WHERE client_id = ?", (client_id,))
    client = cursor.fetchone()

    if not client:
        conn.close()
        return {"error": "Client not found"}

    # 2. Fetch Document Status Checklists for past tax years
    cursor.execute("""
        SELECT tax_year, document_name, status 
        FROM documents_status 
        WHERE client_id = ?
        ORDER BY tax_year DESC
    """, (client_id,))
    checklists = [dict(row) for row in cursor.fetchall()]

    conn.close()

    # Compile raw profile summary text
    raw_profile_text = f"Client Profile: {client['full_name']} (Token: {client['safe_token']}). Document Checklists retrieved from database."

    # Pass through our PII privacy guard before any AI processing
    safe_profile_text = redact_pii(raw_profile_text)

    return {
        "safe_profile": safe_profile_text,
        "client_token": client["safe_token"],
        "checklists": checklists
    }

if __name__ == "__main__":
    # Test retrieval for client_id = 1 (Alice Smith)
    print("Testing retrieval for Client ID 1:")
    data = get_client_organizer_data(1)
    print(data)