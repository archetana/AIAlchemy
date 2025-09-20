#!/bin/bash
set -e

echo "🚀 Starting AIAlchemy Backend"

# For now, use standalone app until we add database infrastructure
# TODO: Switch to main.py when database is configured
echo "🔧 Using standalone app for production (database will be added later)"
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --log-level info