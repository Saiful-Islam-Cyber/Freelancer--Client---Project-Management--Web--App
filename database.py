import sqlite3

DB_NAME = "tracker.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    # Row factory lets us access columns by name like row['title']
    conn.row_factory = sqlite3.Row
    # Enable foreign keys in SQLite
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Clients table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT
        )
    """)
    
    # Create Projects table (added 'paid' column to track payments)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            budget REAL NOT NULL,
            deadline TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            is_paid INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()

def get_dashboard_stats():
    conn = get_db_connection()
    total_clients = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    total_projects = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    completed_projects = conn.execute("SELECT COUNT(*) FROM projects WHERE status = 'Completed'").fetchone()[0]
    
    total_value = conn.execute("SELECT SUM(budget) FROM projects").fetchone()[0] or 0.0
    completed_value = conn.execute("SELECT SUM(budget) FROM projects WHERE status = 'Completed'").fetchone()[0] or 0.0
    
    conn.close()
    return {
        "total_clients": total_clients,
        "total_projects": total_projects,
        "completed_projects": completed_projects,
        "total_value": total_value,
        "completed_value": completed_value
    }
