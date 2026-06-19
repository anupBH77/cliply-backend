#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."

exec gunicorn app.main:app \
    -k uvicorn.workers.UvicornWorker \
    -w 2 \
    -b 0.0.0.0:${PORT:-8000}