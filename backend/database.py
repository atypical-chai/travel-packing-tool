"""
Database module for the Travel Packing List backend.
Uses SQLite (built-in with Python) - no extra install needed.
"""
import json
import os
import sqlite3

# Path to the database file: project/database/items.db (one level up from backend/)
_this_dir = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(_this_dir, "..", "database")
DB_PATH = os.path.join(DB_DIR, "items.db")


def get_db_connection():
    """Connect to the SQLite database. Creates the database folder if it doesn't exist."""
    os.makedirs(DB_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_database():
    """
    Create the items_master table if it doesn't exist.
    Safe to call multiple times (uses IF NOT EXISTS).
    """
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            tags TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_items_by_tags(tags):
    """
    Return all items whose tags array contains at least one of the given tags.
    tags: list of strings, e.g. ["base", "leisure", "summer"]
    Returns: list of dicts with keys id, name, category, tags (tags is a list).
    """
    if not tags:
        return []
    conn = get_db_connection()
    placeholders = ",".join(["?"] * len(tags))
    # json_each(tags) expands the JSON array so we can match any tag
    query = f"""
        SELECT DISTINCT m.id, m.name, m.category, m.tags
        FROM items_master m, json_each(m.tags) je
        WHERE je.value IN ({placeholders})
    """
    cursor = conn.execute(query, tags)
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "name": r[1], "category": r[2], "tags": json.loads(r[3])}
        for r in rows
    ]


def seed_database(items):
    """
    Insert initial items into items_master. Clears existing rows first so
    re-running the seed script gives a clean slate.
    items: list of dicts with keys name, category, tags (tags is a list).
    """
    conn = get_db_connection()
    conn.execute("DELETE FROM items_master")
    for item in items:
        conn.execute(
            "INSERT INTO items_master (name, category, tags) VALUES (?, ?, ?)",
            (item["name"], item["category"], json.dumps(item["tags"])),
        )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_database()
    print(f"Database initialized at: {os.path.abspath(DB_PATH)}")
    print("To seed the database with items, run: python3 items_data.py")
