"""
db.py — handles all SQLite storage for job postings.
Run this file directly once to create the database:
    python db.py
"""

import sqlite3
from datetime import datetime, timedelta

DB_PATH = "jobs.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the jobs table if it doesn't exist yet."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            salary TEXT,
            date_posted TEXT,
            url TEXT,
            first_seen TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Database ready at", DB_PATH)


def save_jobs(jobs: list[dict]) -> int:
    """
    Insert new jobs, skipping duplicates (based on id).
    Returns number of NEW jobs actually inserted.
    """
    conn = get_connection()
    cur = conn.cursor()
    inserted = 0
    for job in jobs:
        try:
            cur.execute("""
                INSERT INTO jobs (id, title, company, location, salary, date_posted, url, first_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job["id"],
                job["title"],
                job["company"],
                job["location"],
                job.get("salary", "Not disclosed"),
                job["date_posted"],
                job["url"],
                datetime.utcnow().isoformat(),
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            # already exists (duplicate id) — skip silently
            continue
    conn.commit()
    conn.close()
    return inserted


def get_recent_jobs(days: int = 7) -> list[dict]:
    """Fetch jobs first_seen in our DB within the last `days` days."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT * FROM jobs WHERE first_seen >= ? ORDER BY first_seen DESC",
        (cutoff,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
