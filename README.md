# Placement & Company Updates Digest 🎯

An automated pipeline that tracks fresh job/hiring data, uses Google Gemini (free LLM API) to summarize trends, and delivers a weekly digest straight to Telegram — no manual checking required.

## How it works

```
Adzuna API (job data) → SQLite (clean, dedupe, store) → Gemini API (summarize trends) → Telegram (deliver)
```

Automated weekly via GitHub Actions — runs even when your laptop is off.

## Setup (do this today — takes ~15 minutes)

### 1. Clone and install
```bash
git clone <your-repo-url>
cd placement-digest
pip install -r requirements.txt
```

### 2. Get your API keys
- **Adzuna** (job data, free): register at https://developer.adzuna.com → get `app_id` and `app_key`
- **Google Gemini** (for summaries, free, no card): get a key at https://aistudio.google.com/apikey
- **Telegram bot**:
  1. Message `@BotFather` on Telegram → `/newbot` → follow prompts → copy the bot token
  2. Search for your new bot, open a chat, send it any message (e.g. "hi")
  3. Run `python get_chat_id.py` to find your chat ID

### 3. Configure
```bash
cp .env.example .env
# then fill in all 5 values in .env
```

### 4. Run it
```bash
python main.py
```
You should get a message on Telegram within a minute.

## Automating it (Week 5-6)

1. Push this repo to GitHub.
2. Go to repo Settings → Secrets and variables → Actions → add all 5 keys from `.env` as repo secrets (same names).
3. The workflow in `.github/workflows/digest.yml` will now run automatically every Monday, or you can trigger it manually from the Actions tab.

## Project structure

| File | Purpose |
|---|---|
| `db.py` | SQLite schema + save/query functions |
| `fetch_jobs.py` | Pulls job postings from Adzuna API |
| `summarize.py` | Sends data to Claude, gets structured JSON digest back |
| `deliver.py` | Sends the final digest via Telegram |
| `main.py` | Orchestrates the full pipeline |
| `.github/workflows/digest.yml` | Weekly automation |

## Customizing

- Edit `QUERIES` in `main.py` to change which roles you track.
- Edit `PROMPT_TEMPLATE` in `summarize.py` to change what the digest highlights (e.g. add salary trend analysis, filter by specific companies you're targeting).

## Why I built this

[Write 2-3 sentences here about your actual motivation — placement season, wanting to save time, etc. This personal note matters in interviews.]
