#!/usr/bin/env bash

# Start a tiny HTTP server so Render sees the service as healthy
python -m http.server 8000 &

# Start celery worker
celery -A app.core.celery_app.celery_app worker -l info -Q monitoring,alerts