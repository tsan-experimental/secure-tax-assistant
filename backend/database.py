import sqlite3
import os

DB_PATH = "data/tax_clients.db"


def init_db():
    """
    Initializes the SQLite database with clients, tax years, and document status checklists.
    """
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop existing tables (children before parents for FK safety)
    cursor.execute("DROP TABLE IF EXISTS checklists")
    cursor.execute("DROP TABLE IF EXISTS tax_years")
    cursor.execute("DROP TABLE IF EXISTS clients")

    # ─── Schema ───────────────────────────────────────────────────────────────

    cursor.execute("""
        CREATE TABLE clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ssn TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE tax_years (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            tax_year INTEGER NOT NULL,
            gross_income REAL,
            filing_status TEXT,
            employer TEXT,
            notes TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(id),
            UNIQUE(client_id, tax_year)
        )
    """)

    cursor.execute("""
        CREATE TABLE checklists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            tax_year INTEGER,
            document_name TEXT,
            status TEXT,
            received_at TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)

    # ─── Seed: Mock Clients ───────────────────────────────────────────────────

    mock_clients = [
        (1, "Alice Smith", "123-45-6789", "alice.smith@example.com", "555-0192"),
        (2, "Bob Jones", "987-65-4321", "bob.jones@example.com", "555-8391"),
        (3, "Charlie Davis", "456-78-9012", "charlie.davis@example.com", "555-4920"),
        (4, "David Miller", "321-43-6543", "david.miller@example.com", "555-9182"),
    ]
    cursor.executemany(
        "INSERT INTO clients (id, name, ssn, email, phone) VALUES (?, ?, ?, ?, ?)",
        mock_clients,
    )

    # ─── Seed: Tax Year Details ───────────────────────────────────────────────

    mock_tax_years = [
        # Alice Smith (ID 1)
        (1, 2023, 88500.00, "married_filing_jointly", "Acme Corp", "W-2 + freelance side gig"),
        (1, 2024, 92300.00, "married_filing_jointly", "Acme Corp", "W-2 + freelance"),
        (1, 2025, 96100.00, "married_filing_jointly", "Acme Corp", "W-2 + freelance + new rental property"),
        # Bob Jones (ID 2)
        (2, 2023, 74200.00, "single", "TechStart Inc", "W-2 only"),
        (2, 2024, 78900.00, "single", "TechStart Inc", "W-2 + consulting 1099-MISC"),
        (2, 2025, 81000.00, "single", "TechStart Inc", "W-2 + consulting"),
        # Charlie Davis (ID 3)
        (3, 2023, 61000.00, "single", "Self-employed (Schedule C)", "Freelance web dev"),
        (3, 2024, 67500.00, "single", "Self-employed (Schedule C)", "Freelance + stock sales"),
        (3, 2025, 72000.00, "single", "Self-employed (Schedule C)", "Freelance + stock sales"),
        # David Miller (ID 4)
        (4, 2023, 105000.00, "married_filing_jointly", "Global Logistics LLC", "W-2 + dividends"),
        (4, 2024, 112400.00, "married_filing_jointly", "Global Logistics LLC", "W-2 + dividends"),
        (4, 2025, 118700.00, "married_filing_jointly", "Global Logistics LLC", "W-2 + dividends + 529 contribution"),
    ]
    cursor.executemany(
        "INSERT INTO tax_years (client_id, tax_year, gross_income, filing_status, employer, notes)"
        " VALUES (?,?,?,?,?,?)",
        mock_tax_years,
    )

    # ─── Seed: Document Checklists ────────────────────────────────────────────

    mock_checklists = [
        # Alice Smith (ID 1)
        (1, 2023, "Form W-2", "Received", "2024-01-15T10:30:00Z"),
        (1, 2023, "Form 1099-INT", "Missing", None),
        (1, 2024, "Form W-2", "Missing", None),
        (1, 2024, "Form 1099-NEC", "Missing", None),
        (1, 2025, "Form W-2", "Missing", None),
        (1, 2025, "Form 1099-NEC", "Missing", None),
        (1, 2025, "Rental-1099", "Missing", None),

        # Bob Jones (ID 2)
        (2, 2023, "Form W-2", "Received", "2024-01-10T09:00:00Z"),
        (2, 2024, "Form W-2", "Received", "2025-01-20T14:15:00Z"),
        (2, 2024, "Form 1099-MISC", "Missing", None),
        (2, 2025, "Form W-2", "Missing", None),
        (2, 2025, "Form 1099-MISC", "Missing", None),

        # Charlie Davis (ID 3)
        (3, 2023, "Form 1099-NEC", "Missing", None),
        (3, 2024, "Form W-2", "Missing", None),
        (3, 2024, "Schedule C", "Missing", None),
        (3, 2025, "Schedule C", "Missing", None),
        (3, 2025, "Form 1099-NEC", "Missing", None),

        # David Miller (ID 4)
        (4, 2023, "Form W-2", "Received", "2024-01-05T11:00:00Z"),
        (4, 2024, "Form W-2", "Received", "2025-01-18T16:45:00Z"),
        (4, 2024, "Form 1099-DIV", "Received", "2025-02-01T08:30:00Z"),
        (4, 2025, "Form W-2", "Missing", None),
        (4, 2025, "Form 1099-DIV", "Missing", None),
        (4, 2025, "Form 5498", "Missing", None),
    ]
    cursor.executemany(
        "INSERT INTO checklists (client_id, tax_year, document_name, status, received_at) VALUES (?, ?, ?, ?, ?)",
        mock_checklists,
    )

    conn.commit()
    conn.close()
    print("Database initialized and seeded with 4 mock clients successfully!")


if __name__ == "__main__":
    init_db()
