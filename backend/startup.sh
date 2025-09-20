#!/bin/bash
set -e

echo "🚀 Starting AIAlchemy Backend"

# Run database migrations
if [[ "$ENVIRONMENT" == "production" || "$ENVIRONMENT" == "staging" ]]; then
    echo "📊 Running database migrations"
    alembic upgrade head
fi

# Start the FastAPI application
echo "🌟 Starting FastAPI server"
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers ${WORKERS:-1} \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-log \
    --log-level info