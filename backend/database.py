import sqlite3
import os

DB_PATH = "data/tax_clients.db"

def init_db():
    """
    Initialize the SQLite database and create necessary tables for clients, 
    tax years, and document statuses.
    """
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table 1: Clients
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        client_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        safe_token TEXT NOT NULL
    )
    """)

    # Table 2: Tax Years & Organizers
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tax_years (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        tax_year INTEGER,
        filing_status TEXT,
        FOREIGN KEY (client_id) REFERENCES clients (client_id)
    )
    """)

    # Table 3: Document Status Checklists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        tax_year INTEGER,
        document_name TEXT,
        status TEXT, -- e.g., 'Missing', 'Received'
        FOREIGN KEY (client_id) REFERENCES clients (client_id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully at", DB_PATH)

def seed_db():
    """
    Seed the database with mock client records and missing document checklists[cite: 1].
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if data already exists to avoid duplication
    cursor.execute("SELECT COUNT(*) FROM clients")
    if cursor.fetchone()[0] > 0:
        print("Database already seeded.")
        conn.close()
        return

    # Insert mock clients[cite: 1]
    clients = [
        ("Alice Smith", "alice@example.com", "CLIENT_TOKEN_001"),
        ("Bob Johnson", "bob@example.com", "CLIENT_TOKEN_002"),
        ("Carol Williams", "carol@example.com", "CLIENT_TOKEN_003")
    ]
    cursor.executemany("INSERT INTO clients (full_name, email, safe_token) VALUES (?, ?, ?)", clients)

    # Insert mock checklists for tax years 2023, 2024, 2025[cite: 1]
    checklists = [
        # Alice Smith (client_id = 1)
        (1, 2023, "Form W-2", "Received"),
        (1, 2023, "Form 1099-INT", "Missing"),
        (1, 2024, "Form W-2", "Missing"),
        (1, 2024, "Form 1099-NEC", "Missing"),
        
        # Bob Johnson (client_id = 2)
        (2, 2024, "Form W-2", "Received"),
        (2, 2024, "Form 1098 (Mortgage)", "Missing"),
        (2, 2025, "Quarterly Estimated Tax Vouchers", "Missing"),

        # Carol Williams (client_id = 3)
        (3, 2023, "Schedule C (Business Income)", "Received"),
        (3, 2024, "Schedule C (Business Income)", "Missing"),
        (3, 2024, "Form 1099-K", "Missing")
    ]
    cursor.executemany("""
    INSERT INTO documents_status (client_id, tax_year, document_name, status)
    VALUES (?, ?, ?, ?)
    """, checklists)

    conn.commit()
    conn.close()
    print("Mock client data seeded successfully!")

if __name__ == "__main__":
    init_db()
    seed_db()