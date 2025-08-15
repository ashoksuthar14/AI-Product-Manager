# AI Product Manager – Multi‑Agent System

A multi‑agent product planning and analysis app built with Flask, Flask‑SocketIO, SQLAlchemy, and CrewAI/Gemini. It provides real‑time project analysis, planning assistance, and automation suggestions via a web UI.

## Features

- Multi‑agent collaboration (Product Manager, Developer, QA, AI Engineer)
- Real‑time analysis updates over WebSockets
- Project planning, risk assessment, and automation suggestions
- Modular architecture with clear separation of routes, services, models, and agents

## Quick start

1) Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2) Install dependencies
```bash
pip install -r requirements.txt
```

3) Configure environment
Create a `.env` file in the project root:
```bash
SECRET_KEY=change-me
# Gemini / Google Generative AI
# Provide either a single key or a comma-separated list
GEMINI_API_KEY=your-key
# or
# GEMINI_API_KEYS=key1,key2,key3

# Optional DB override (defaults to sqlite:///app.db)
# DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

4) Run the app (development)
```bash
python run.py
```
The app will start with Flask‑SocketIO’s development server.

5) Run a lightweight check
```bash
python test_automation.py
```
This exercises the automation builders without calling external LLMs.

## Production

Flask‑SocketIO requires an async worker (eventlet or gevent) in production. One minimal option:
```bash
pip install eventlet gunicorn
export GEMINI_API_KEY=your-key
export SECRET_KEY=change-me
# create the DB on first run
python -c "from app import create_app; app = create_app();\nfrom app import db;\nfrom flask import current_app;\n\nprint('DB ready')"
# run the server
gunicorn -k eventlet -w 1 -b 0.0.0.0:8000 run:app
```

## Project structure

```
.
├── app/
│   ├── __init__.py           # Flask app factory, db, socketio
│   ├── agents/               # Multi‑agent logic
│   ├── llm/                  # LLM client wrapper
│   ├── models/               # SQLAlchemy models
│   ├── routes/               # Blueprints (main, projects, automation, voice)
│   ├── services/             # Domain services
│   ├── static/               # Static assets
│   └── templates/            # Jinja templates
├── config.py                 # App config + .env loader
├── requirements.txt
├── run.py                    # Entrypoint (SocketIO)
├── test_automation.py        # Safe demo test (no LLM calls)
├── test_collaborative_agents.py  # Uses LLM (needs keys)
├── test_llm.py               # Direct LLM test (needs keys)
└── app.db                    # Local SQLite (created at first run)
```

## CI and Docs (GitHub Actions + Pages)

- A CI workflow compiles the code and runs a safe smoke test (`test_automation.py`).
- Documentation is built with MkDocs and deployed to GitHub Pages via Actions. After pushing this repo to GitHub, enable Pages in the repo settings if needed. The Pages environment URL will appear on workflow runs.

Local docs preview (optional):
```bash
pip install mkdocs mkdocs-material
mkdocs serve  # then open http://127.0.0.1:8000
```

## Environment and Security

- Never commit API keys. Keys are now read from environment variables (`GEMINI_API_KEY` or `GEMINI_API_KEYS`).
- If keys are missing, LLM‑dependent features gracefully fall back to built‑in defaults.

## Troubleshooting

- SocketIO in production: use eventlet or gevent workers.
- If you see LLM errors, verify `GEMINI_API_KEY` (or `GEMINI_API_KEYS`) is set in the environment (or `.env`) and is valid.
- For DB migrations or external databases, set `DATABASE_URL` accordingly.

## License

MIT License 