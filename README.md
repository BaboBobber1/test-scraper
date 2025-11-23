# Crypto YouTube Harvester

A full-stack FastAPI + React application to discover and enrich crypto-related YouTube channels without relying on the official Data API.

## Backend

- Python 3.11, FastAPI, SQLAlchemy (async SQLite)
- Scraping via httpx and HTML parsing
- Entry point: `uvicorn backend.main:app --reload`

## Frontend

- React + TypeScript + Vite
- TailwindCSS utility styling
- Dev server: `npm run dev`

## Getting Started

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

In another terminal:

```bash
npm install
npm run dev
```

Open http://localhost:5173 and click **Quickstart** to begin discovery.
