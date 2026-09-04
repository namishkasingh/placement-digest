"""
summarize.py — feeds recent jobs to Google Gemini (free API) and gets back a structured digest.

Test it directly (after db.py has some data in it):
    python summarize.py
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3.6-flash"  # free tier, fast, generous daily limit
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

PROMPT_TEMPLATE = """You are helping a 3rd-year B.Tech student track placement-relevant hiring trends.

Here is a list of job postings collected in the last 7 days (JSON):
{jobs_json}

Analyze this data and respond with ONLY valid JSON (no markdown, no extra text) in this exact format:
{{
  "total_new_openings": <number>,
  "top_hiring_companies": ["company1", "company2", "company3"],
  "most_in_demand_roles": ["role1", "role2", "role3"],
  "notable_trend": "one sentence about a pattern you noticed (location, salary, role type, etc.)",
  "highlighted_openings": [
    {{"title": "...", "company": "...", "why_relevant": "one short reason a fresher/final-year student should look at this"}}
  ]
}}

Pick at most 3 highlighted_openings. If the data is too sparse for a field, use reasonable empty values (empty list, "Not enough data" etc.) instead of making things up.
"""


def generate_digest(jobs: list[dict]) -> dict:
    """Send recent jobs to Claude and get back a structured digest dict."""
    if not jobs:
        return {
            "total_new_openings": 0,
            "top_hiring_companies": [],
            "most_in_demand_roles": [],
            "notable_trend": "No new jobs collected this period.",
            "highlighted_openings": [],
        }

    # Keep payload small — just the fields the model actually needs
    trimmed = [
        {"title": j["title"], "company": j["company"], "location": j["location"], "salary": j["salary"]}
        for j in jobs
    ]

    prompt = PROMPT_TEMPLATE.format(jobs_json=json.dumps(trimmed, indent=2))

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 2048},
    }
    resp = requests.post(
        GEMINI_URL,
        params={"key": GEMINI_API_KEY},
        json=payload,
        timeout=30,
    )

    if resp.status_code != 200:
        print(f"Gemini API error: {resp.status_code} - {resp.text[:300]}")
        return {"error": "api_call_failed", "detail": resp.text[:300]}

    data = resp.json()
    try:
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        print("Warning: unexpected Gemini response shape:", data)
        return {"error": "unexpected_response", "raw": data}

    # Safety: strip markdown code fences if the model adds them anyway
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        print("Warning: could not parse model output as JSON. Raw output:")
        print(raw_text)
        return {"error": "parse_failed", "raw": raw_text}


def format_digest_text(digest: dict) -> str:
    """Turn the digest dict into a readable message for Telegram/email."""
    lines = ["📊 *Weekly Placement Digest*\n"]
    lines.append(f"🔹 New openings tracked: {digest.get('total_new_openings', 0)}")

    companies = digest.get("top_hiring_companies", [])
    if companies:
        lines.append(f"🔹 Top hiring companies: {', '.join(companies)}")

    roles = digest.get("most_in_demand_roles", [])
    if roles:
        lines.append(f"🔹 In-demand roles: {', '.join(roles)}")

    trend = digest.get("notable_trend")
    if trend:
        lines.append(f"\n📈 Trend: {trend}")

    highlights = digest.get("highlighted_openings", [])
    if highlights:
        lines.append("\n⭐ Worth checking out:")
        for h in highlights:
            lines.append(f"- {h.get('title')} @ {h.get('company')} — {h.get('why_relevant')}")

    return "\n".join(lines)


if __name__ == "__main__":
    from db import get_recent_jobs
    jobs = get_recent_jobs(days=7)
    digest = generate_digest(jobs)
    print(format_digest_text(digest))
