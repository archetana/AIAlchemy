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

# Verify SUP and construct database URL
if [ "$USE_SUPABASE" = "true" ]; then
    echo "🔗 Supabase storage enabled"
    if [ -n "$SUPABASE_URL" ] && [ -n "$SUPABASE_ANON_KEY" ] && [ -n "$DATABASE_URL" ]; then
        echo "✅ Supabase credentials found"
    else
        echo "⚠️ Supabase enabled but no credentials found"
    fi
fi

# Verify SQLite configuration and construct database URL
if [ "$USE_SQLITE" = "true" ]; then
    echo "🗂️ SQLite storage enabled"
    if [ -n "$SQLITE_DATABASE_URL" ]; then
        echo "✅ SQLite database URL found"
        DATABASE_URL="$SQLITE_DATABASE_URL"
        # Initialize database on startup (reliable sync method)
        echo "🔧 Creating database tables..."
        python3 create_tables_sync.py || echo "⚠️ Table creation warning"

        # Also run the standalone init for sample data
        echo "🔧 Adding sample data..."
        python3 init_db_standalone.py || echo "⚠️ Sample data init warning"
    else
        echo "⚠️ SQLite enabled but no database URL found"
    fi
fi



# Start the application
echo "✅ Starting FastAPI application"
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8080} \
    --log-level info