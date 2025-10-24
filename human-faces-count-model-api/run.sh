#!/bin/bash
source venv/bin/activate

# Start Celery worker in background
echo "Starting Celery Faces Processing Worker..."
celery -A app.celery_app.celery_app worker --loglevel=info &

# Start FastAPI app
echo "Starting Faces Count FastAPI Server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000