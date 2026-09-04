"""
main.py — runs the full pipeline end to end:
    fetch -> store -> summarize -> deliver

Run it:
    python main.py
"""

from db import init_db, save_jobs, get_recent_jobs
from fetch_jobs import fetch_jobs
from summarize import generate_digest, format_digest_text
from deliver import send_telegram_message

# Tune these to match roles relevant to YOUR placements
QUERIES = [
    "software engineer fresher",
    "software developer trainee",
    "data analyst fresher",
]


def run():
    print("Step 1/4: Making sure database exists...")
    init_db()

    print("Step 2/4: Fetching fresh job postings...")
    total_new = 0
    for query in QUERIES:
        jobs = fetch_jobs(query=query, pages=1)
        new_count = save_jobs(jobs)
        total_new += new_count
        print(f"  '{query}': fetched {len(jobs)}, {new_count} new")

    print(f"Total new jobs added this run: {total_new}")

    print("Step 3/4: Generating AI digest...")
    recent_jobs = get_recent_jobs(days=7)
    digest = generate_digest(recent_jobs)
    digest_text = format_digest_text(digest)
    print("\n--- DIGEST ---")
    print(digest_text)
    print("--- END DIGEST ---\n")

    print("Step 4/4: Sending digest...")
    send_telegram_message(digest_text)

    print("Done.")


if __name__ == "__main__":
    run()
