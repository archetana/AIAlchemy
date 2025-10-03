#!/bin/bash
set -e

echo "🚀 Starting AIAlchemy Backend"

# Initialize database on startup
echo "🔧 Initializing database..."
python3 init_db_standalone.py || echo "⚠️ Database init warning (may already exist)"

# Start the application
echo "✅ Starting FastAPI application"
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --log-level info