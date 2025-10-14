@echo off
REM Local Development Server Starter for Windows
echo.
echo ========================================
echo AIAlchemy Local Development Setup
echo ========================================
echo.

REM Check if backend directory exists
if not exist "backend\" (
    echo ERROR: backend directory not found!
    echo Please run this script from the project root directory.
    pause
    exit /b 1
)

REM Check if frontend directory exists
if not exist "frontend\" (
    echo ERROR: frontend directory not found!
    echo Please run this script from the project root directory.
    pause
    exit /b 1
)

echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.12+ from python.org
    pause
    exit /b 1
)
python --version

echo.
echo [2/6] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH!
    echo Please install Node.js from nodejs.org
    pause
    exit /b 1
)
node --version
npm --version

echo.
echo [3/6] Installing backend dependencies...
cd backend
if not exist ".env" (
    echo WARNING: .env file not found in backend directory
    echo Creating from .env.local.example...
    if exist ".env.local.example" (
        copy .env.local.example .env
        echo Created .env file. Please edit it with your settings.
    ) else (
        echo ERROR: .env.local.example not found!
    )
)

echo Installing Python packages...
pip install -q sqlalchemy alembic aiosqlite fastapi uvicorn pydantic python-jose passlib bcrypt python-multipart structlog python-dotenv
if errorlevel 1 (
    echo WARNING: Some packages failed to install. Trying minimal install...
    pip install fastapi uvicorn sqlalchemy aiosqlite
)

echo.
echo [4/6] Initializing local database...
if not exist "aialchemy_local.db" (
    echo Database not found, creating...
    python -c "from app.init_db_unified import init_database; import asyncio; asyncio.run(init_database())" 2>nul
    if errorlevel 1 (
        echo Database initialization failed or not needed yet.
    )
)

cd ..

echo.
echo [5/6] Installing frontend dependencies...
cd frontend
if not exist ".env" (
    echo Creating frontend .env file...
    echo REACT_APP_API_BASE_URL=http://localhost:8000 > .env
)

if not exist "node_modules\" (
    echo Installing npm packages (this may take a few minutes)...
    call npm install
) else (
    echo node_modules found, skipping npm install
)

cd ..

echo.
echo [6/6] Starting development servers...
echo.
echo ========================================
echo IMPORTANT:
echo - Backend will start on http://localhost:8000
echo - Frontend will start on http://localhost:3000
echo - Press Ctrl+C in each window to stop servers
echo ========================================
echo.
echo Opening terminals...
echo.

REM Start backend in new window
start "AIAlchemy Backend (http://localhost:8000)" cmd /k "cd backend && echo Starting Backend Server... && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
start "AIAlchemy Frontend (http://localhost:3000)" cmd /k "cd frontend && echo Starting Frontend Server... && npm start"

echo.
echo ========================================
echo Development servers are starting!
echo ========================================
echo.
echo Two new terminal windows have opened:
echo 1. Backend API server (http://localhost:8000)
echo 2. Frontend React app (http://localhost:3000)
echo.
echo Wait for both to finish starting, then open:
echo http://localhost:3000
echo.
echo To stop servers: Close the terminal windows or press Ctrl+C
echo.
echo Check docs/setup/DEVELOPMENT_SETUP.md for more details
echo ========================================
pause
