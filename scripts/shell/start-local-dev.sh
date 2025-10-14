#!/bin/bash
# Local Development Server Starter for Linux/Mac

echo ""
echo "========================================"
echo "AIAlchemy Local Development Setup"
echo "========================================"
echo ""

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "ERROR: backend directory not found!"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo "ERROR: frontend directory not found!"
    echo "Please run this script from the project root directory."
    exit 1
fi

echo "[1/6] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3.12+ from python.org"
    exit 1
fi
python3 --version

echo ""
echo "[2/6] Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed!"
    echo "Please install Node.js from nodejs.org"
    exit 1
fi
node --version
npm --version

echo ""
echo "[3/6] Installing backend dependencies..."
cd backend

if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found in backend directory"
    echo "Creating from .env.local.example..."
    if [ -f ".env.local.example" ]; then
        cp .env.local.example .env
        echo "Created .env file. Please edit it with your settings."
    else
        echo "ERROR: .env.local.example not found!"
    fi
fi

echo "Installing Python packages..."
pip3 install -q sqlalchemy alembic aiosqlite fastapi uvicorn pydantic python-jose passlib bcrypt python-multipart structlog python-dotenv 2>/dev/null || {
    echo "WARNING: Some packages failed to install. Trying minimal install..."
    pip3 install fastapi uvicorn sqlalchemy aiosqlite
}

echo ""
echo "[4/6] Initializing local database..."
if [ ! -f "aialchemy_local.db" ]; then
    echo "Database not found, creating..."
    python3 -c "from app.init_db_unified import init_database; import asyncio; asyncio.run(init_database())" 2>/dev/null || {
        echo "Database initialization failed or not needed yet."
    }
fi

cd ..

echo ""
echo "[5/6] Installing frontend dependencies..."
cd frontend

if [ ! -f ".env" ]; then
    echo "Creating frontend .env file..."
    echo "REACT_APP_API_BASE_URL=http://localhost:8000" > .env
fi

if [ ! -d "node_modules" ]; then
    echo "Installing npm packages (this may take a few minutes)..."
    npm install
else
    echo "node_modules found, skipping npm install"
fi

cd ..

echo ""
echo "[6/6] Starting development servers..."
echo ""
echo "========================================"
echo "IMPORTANT:"
echo "- Backend will start on http://localhost:8000"
echo "- Frontend will start on http://localhost:3000"
echo "- Press Ctrl+C to stop both servers"
echo "========================================"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo "Starting Backend Server..."
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting Frontend Server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "Development servers are running!"
echo "========================================"
echo ""
echo "Backend PID: $BACKEND_PID (http://localhost:8000)"
echo "Frontend PID: $FRONTEND_PID (http://localhost:3000)"
echo ""
echo "Open http://localhost:3000 in your browser"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "========================================"

# Wait for user to press Ctrl+C
wait
