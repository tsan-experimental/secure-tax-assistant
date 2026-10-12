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

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ssn TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checklists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            tax_year INTEGER,
            document_name TEXT,
            status TEXT,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    """)

    # Clear existing mock data to prevent duplicates on restart
    cursor.execute("DELETE FROM checklists")
    cursor.execute("DELETE FROM clients")

    # Seed 4 mock clients (multiple realistic profiles)
    mock_clients = [
        (1, "Alice Smith", "123-45-6789", "alice.smith@example.com", "555-0192"),
        (2, "Bob Jones", "987-65-4321", "bob.jones@example.com", "555-8391"),
        (3, "Charlie Davis", "456-78-9012", "charlie.davis@example.com", "555-4920"),
        (4, "David Miller", "321-43-6543", "david.miller@example.com", "555-9182")
    ]
    cursor.executemany("INSERT INTO clients (id, name, ssn, email, phone) VALUES (?, ?, ?, ?, ?)", mock_clients)

    # Seed mock document checklists for previous tax years (2023, 2024)
    mock_checklists = [
        # Alice Smith (ID 1)
        (1, 2024, "Form W-2", "Missing"),
        (1, 2024, "Form 1099-NEC", "Missing"),
        (1, 2023, "Form W-2", "Received"),
        (1, 2023, "Form 1099-INT", "Missing"),
        
        # Bob Jones (ID 2)
        (2, 2024, "Form W-2", "Received"),
        (2, 2024, "Form 1099-MISC", "Missing"),
        (2, 2023, "Form W-2", "Received"),
        
        # Charlie Davis (ID 3)
        (3, 2024, "Form W-2", "Missing"),
        (3, 2024, "Schedule C", "Missing"),
        (3, 2023, "Form 1099-NEC", "Missing"),
        
        # David Miller (ID 4)
        (4, 2024, "Form W-2", "Received"),
        (4, 2024, "Form 1099-DIV", "Received"),
        (4, 2023, "Form W-2", "Received")
    ]
    cursor.executemany("INSERT INTO checklists (client_id, tax_year, document_name, status) VALUES (?, ?, ?, ?)", mock_checklists)

    conn.commit()
    conn.close()
    print("Database initialized and seeded with multiple mock clients successfully!")

if __name__ == "__main__":
    init_db()