#!/bin/bash

# Production startup script using gunicorn with Uvicorn workers

APP_MODULE="app.core.server:app"
HOST="0.0.0.0"
PORT="8002"
WORKERS=$(python3 -c "import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)")

echo "🚀 Starting FastAPI app with Gunicorn on $HOST:$PORT with $WORKERS workers..."

exec gunicorn "$APP_MODULE" \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers "$WORKERS" \
    --bind "$HOST:$PORT"
