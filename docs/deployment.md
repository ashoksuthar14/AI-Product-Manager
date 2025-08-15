# Deployment

## GitHub Pages (Docs)
This repository publishes documentation to GitHub Pages via Actions. After pushing to GitHub:
- Ensure Pages is enabled in repository settings
- The workflow `pages.yml` will build MkDocs and deploy to the Pages environment

## App hosting (Flask)
GitHub Pages cannot host dynamic Flask apps. Use a platform like Render, Railway, Fly.io, or your own server.

Minimal production run locally:
```bash
pip install eventlet gunicorn
export GEMINI_API_KEY=your-key
export SECRET_KEY=change-me
gunicorn -k eventlet -w 1 -b 0.0.0.0:8000 run:app
```

For container deployments, create a Dockerfile and deploy to your preferred platform. Add secrets (API keys) via the platform's environment settings.