# Deployment Guide

## Local
```bash
cd sneaker-ecommerce
python3 -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt
PYTHONPATH=. python database/init_db.py
PYTHONPATH=. python backend/run.py
```

## Production Checklist
- Set strong `SECRET_KEY` via environment
- Switch `DATABASE_URL` to PostgreSQL
- Run with Gunicorn: `gunicorn -w 4 "backend.app:create_app()"`
- Nginx reverse proxy + SSL
- Never commit the SQLite file or secrets
