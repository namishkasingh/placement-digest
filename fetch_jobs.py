"""
fetch_jobs.py — pulls job postings from the Adzuna API.

Test it directly:
    python fetch_jobs.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search"  # "in" = India


def fetch_jobs(query: str = "software engineer", location: str = "", pages: int = 2) -> list[dict]:
    """
    Fetch jobs matching `query` from Adzuna, across `pages` of results.
    Returns a cleaned list of dicts ready for storage.
    """
    all_jobs = []

    for page in range(1, pages + 1):
        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "results_per_page": 20,
            "what": query,
            "where": location,
            "content-type": "application/json",
        }
        resp = requests.get(f"{BASE_URL}/{page}", params=params, timeout=15)

        if resp.status_code != 200:
            print(f"Adzuna API error on page {page}: {resp.status_code} - {resp.text[:200]}")
            break

        data = resp.json()
        results = data.get("results", [])

        if not results:
            break  # no more pages

        for r in results:
            all_jobs.append({
                "id": str(r.get("id")),
                "title": r.get("title", "").strip(),
                "company": r.get("company", {}).get("display_name", "Unknown"),
                "location": r.get("location", {}).get("display_name", "Unknown"),
                "salary": _format_salary(r),
                "date_posted": r.get("created", ""),
                "url": r.get("redirect_url", ""),
            })

    return all_jobs


def _format_salary(r: dict) -> str:
    lo = r.get("salary_min")
    hi = r.get("salary_max")
    if lo and hi:
        return f"₹{int(lo):,} - ₹{int(hi):,}"
    return "Not disclosed"


if __name__ == "__main__":
    jobs = fetch_jobs(query="software engineer fresher", pages=1)
    print(f"Fetched {len(jobs)} jobs\n")
    for j in jobs[:5]:
        print(f"- {j['title']} @ {j['company']} ({j['location']}) - {j['salary']}")
