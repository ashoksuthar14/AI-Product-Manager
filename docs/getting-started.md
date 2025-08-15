# Getting Started

## Prerequisites
- Python 3.11+
- A Google Generative AI key (Gemini)

## Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:
```bash
SECRET_KEY=change-me
GEMINI_API_KEY=your-key
# or multiple keys
# GEMINI_API_KEYS=key1,key2
```

## Run
```bash
python run.py
```
Open http://127.0.0.1:5000

## Smoke test
```bash
python test_automation.py
```