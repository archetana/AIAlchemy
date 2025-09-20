#!/bin/bash
set -e

echo "🚀 Starting AIAlchemy Backend (Standalone Mode)"
echo "🌟 Starting FastAPI server on port ${PORT:-8000}"

# Use completely isolated standalone app with zero external dependencies
echo "🔧 Using standalone FastAPI app (completely isolated)"
exec uvicorn app.standalone:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --log-level info