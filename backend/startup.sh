#!/bin/bash
set -e

echo "🚀 Starting AIAlchemy Backend"

# Handle GCS authentication if base64 key is provided
if [ -n "$GCS_SERVICE_ACCOUNT_KEY_BASE64" ]; then
    echo "🔑 Setting up GCS authentication from base64 key..."
    echo "$GCS_SERVICE_ACCOUNT_KEY_BASE64" | base64 -d > /tmp/gcs-service-account-key.json
    export GOOGLE_APPLICATION_CREDENTIALS="/tmp/gcs-service-account-key.json"
    echo "✅ GCS authentication configured"
else
    echo "ℹ️ No base64 GCS key found, using default authentication"
fi

# Verify GCS configuration
if [ "$USE_GOOGLE_CLOUD_STORAGE" = "true" ]; then
    echo "🗂️ GCS storage enabled for bucket: $GOOGLE_CLOUD_STORAGE_BUCKET"
    if [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ] && [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
        echo "✅ GCS credentials file found"
    else
        echo "⚠️ GCS enabled but no credentials file found"
    fi
else
    echo "📁 Using local file storage"
fi

# Initialize database on startup
echo "🔧 Initializing database..."
python3 -c "
import asyncio
from app.database import engine
from app.models import Base

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print('✅ Database tables created successfully')

asyncio.run(create_tables())
" || echo "⚠️ Database init warning"

# Also run the standalone init for sample data
python3 init_db_standalone.py || echo "⚠️ Sample data init warning"

# Start the application
echo "✅ Starting FastAPI application"
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --log-level info