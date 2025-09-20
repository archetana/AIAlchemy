#!/bin/bash
set -e

echo "🚀 Starting AIAlchemy Backend"

# Run database migrations
if [[ "$ENVIRONMENT" == "production" || "$ENVIRONMENT" == "staging" ]]; then
    echo "📊 Running database migrations"
    alembic upgrade head
fi

# Start the FastAPI application
echo "🌟 Starting FastAPI server on port ${PORT:-8000}"

# For deployment verification, use simple app first
echo "🔧 Using simple FastAPI app for deployment verification"
exec uvicorn app.main_simple:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --log-level info