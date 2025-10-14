# Local Development Setup Guide

This guide will help you set up and run AIAlchemy locally for development and testing.

## Prerequisites

- ✅ Python 3.12+ (Installed)
- ✅ Node.js 22.19+ (Installed)
- ✅ npm 10.9+ (Installed)

## Quick Start (For Testing Changes Locally)

### Option 1: Quick Development Mode (Recommended)

Run both servers with a single command:

```bash
# From the root directory
npm run dev
```

This will start:
- Backend API server on http://localhost:8000
- Frontend React app on http://localhost:3000

### Option 2: Manual Setup (Step by Step)

#### Step 1: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Note**: If you get errors installing all dependencies (especially ML packages), use the minimal requirements:

```bash
pip install -r requirements-minimal.txt
```

#### Step 2: Setup Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cd backend
cp .env.local.example .env
```

Edit `.env` with your settings:
```env
# Environment
ENVIRONMENT=development

# Database (SQLite for local development)
DATABASE_URL=sqlite+aiosqlite:///./aialchemy_local.db

# JWT Secret (generate a random string)
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS (allow frontend)
CORS_ORIGINS=http://localhost:3000

# Optional: Disable Supabase for local dev
USE_SUPABASE=false
```

#### Step 3: Initialize Local Database

```bash
cd backend
python -c "from app.init_db_unified import init_database; import asyncio; asyncio.run(init_database())"
```

Or use the init script:
```bash
python init_database.py
```

#### Step 4: Start Backend Server

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
🚀 Starting AIAlchemy API server...
✅ Database connected successfully
📊 AIAlchemy API ready
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Test the backend**: Open http://localhost:8000 in your browser

#### Step 5: Install Frontend Dependencies

Open a **new terminal** and run:

```bash
cd frontend
npm install
```

#### Step 6: Setup Frontend Environment

Create a `.env` file in the `frontend` directory:

```bash
cd frontend
echo "REACT_APP_API_BASE_URL=http://localhost:8000" > .env
```

Or create `.env` manually with:
```env
REACT_APP_API_BASE_URL=http://localhost:8000
```

#### Step 7: Start Frontend Server

```bash
cd frontend
npm start
```

The app will open automatically at http://localhost:3000

## Testing the Registration Fix

1. Open http://localhost:3000/register
2. Fill in the registration form:
   - Full Name: Test User
   - Job Title: Engineer
   - Email: test@example.com
   - Password: MyPass123!
   - Phone: +1234567890 (optional)
   - Role: Select any role
3. Click "Create Account"
4. ✅ You should be automatically logged in and redirected to the dashboard
5. ✅ Check browser localStorage for tokens (press F12 > Application > Local Storage)

## Common Issues & Solutions

### Issue: Backend says "ModuleNotFoundError: No module named 'sqlalchemy'"

**Solution**: Install dependencies
```bash
cd backend
pip install sqlalchemy alembic aiosqlite
```

Or install all:
```bash
pip install -r requirements.txt
```

### Issue: Frontend can't connect to backend (CORS errors)

**Solution**: Make sure backend `.env` has correct CORS settings:
```env
CORS_ORIGINS=http://localhost:3000
```

### Issue: Database errors on backend startup

**Solution**: Delete the database and reinitialize:
```bash
cd backend
rm aialchemy_local.db
python init_database.py
```

### Issue: Port 8000 or 3000 already in use

**Solution**: Kill the process or use different ports
```bash
# For backend on port 8001
uvicorn app.main:app --reload --port 8001

# For frontend on port 3001
PORT=3001 npm start
```

Then update frontend `.env`:
```env
REACT_APP_API_BASE_URL=http://localhost:8001
```

### Issue: Frontend build errors or dependency issues

**Solution**: Clear cache and reinstall
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Development Workflow

### 1. Make Code Changes

Edit files in your IDE:
- Backend: `backend/app/`
- Frontend: `frontend/src/`

### 2. Test Locally

- Backend will auto-reload when you save files (uvicorn --reload)
- Frontend will hot-reload automatically (React dev server)
- Test in browser at http://localhost:3000

### 3. Check Logs

**Backend logs** (in terminal running uvicorn):
- See request logs, errors, and debug info
- Look for validation errors, database errors, etc.

**Frontend logs** (in browser console F12):
- See React errors, API responses, state changes
- Check Network tab for API calls

### 4. Commit When Ready

Only commit when everything works locally:
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

## Useful Development Commands

### Backend

```bash
# Run with auto-reload (default)
cd backend
uvicorn app.main:app --reload

# Run with debug logs
uvicorn app.main:app --reload --log-level debug

# Check API documentation
# Open http://localhost:8000/docs

# Run tests
pytest

# Check specific endpoint
curl http://localhost:8000/health
```

### Frontend

```bash
# Start dev server
cd frontend
npm start

# Build for production (test if it builds)
npm run build

# Run linter
npm run lint

# Run tests
npm test
```

### Database

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Check database
python -c "from app.core.database import database_manager; print(database_manager)"

# Create test user
python create_test_user.py
```

## Quick Testing Checklist

Before pushing to GitHub, test these locally:

- [ ] Backend starts without errors: `uvicorn app.main:app --reload`
- [ ] Frontend starts without errors: `npm start`
- [ ] Registration works with valid password
- [ ] Registration shows error with invalid password
- [ ] Registration respects role selection
- [ ] User is automatically logged in after registration
- [ ] Tokens are stored in localStorage
- [ ] Dashboard loads after login
- [ ] Logout works correctly
- [ ] Login works with registered user

## Environment Variables Reference

### Backend `.env`

```env
# Required
ENVIRONMENT=development
DATABASE_URL=sqlite+aiosqlite:///./aialchemy_local.db
JWT_SECRET=your-secret-key-min-32-chars
CORS_ORIGINS=http://localhost:3000

# Optional
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
REFRESH_TOKEN_EXPIRATION_DAYS=30
USE_SUPABASE=false
LOG_LEVEL=INFO
```

### Frontend `.env`

```env
# Required
REACT_APP_API_BASE_URL=http://localhost:8000

# Optional
REACT_APP_ENV=development
```

## Tips for Fast Development

1. **Keep both servers running** - Backend and frontend will auto-reload on changes
2. **Use browser DevTools** (F12) - Check console, network, and application tabs
3. **Watch backend terminal** - See real-time logs and errors
4. **Test before committing** - Always verify locally first
5. **Use separate terminals** - One for backend, one for frontend
6. **Clear browser cache** - If you see stale data (Ctrl+Shift+R)
7. **Check localStorage** - Verify tokens are stored correctly

## Database Locations

- **Local Development**: `backend/aialchemy_local.db` (SQLite)
- **Production**: Supabase (PostgreSQL)

To switch between databases, change `DATABASE_URL` in `.env`

## API Documentation

Once backend is running, visit:
- **Interactive API docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative docs**: http://localhost:8000/redoc (ReDoc)
- **Health check**: http://localhost:8000/health
- **API status**: http://localhost:8000/api/status

## Debugging Tips

### Backend Debugging

Add debug prints in your code:
```python
import structlog
logger = structlog.get_logger()

logger.info("Debug info", variable=value)
logger.error("Error info", error=str(e))
```

### Frontend Debugging

Add console logs:
```javascript
console.log('Debug info:', variable);
console.error('Error:', error);
```

Or use React DevTools browser extension

### Network Debugging

In browser DevTools (F12) > Network tab:
- See all API requests
- Check request/response headers
- View request payload and response data
- Check status codes (200, 400, 500, etc.)

## Next Steps

1. **Start both servers locally**
2. **Make your changes**
3. **Test thoroughly in browser**
4. **Check logs for errors**
5. **Only then commit and push**

This saves deployment time and ensures everything works before going to production! 🚀

## Additional Resources

- FastAPI Docs: https://fastapi.tiangolo.com/
- React Docs: https://react.dev/
- SQLAlchemy Docs: https://docs.sqlalchemy.org/
- Material-UI Docs: https://mui.com/

---

**Need Help?** Check the logs first, then review error messages in browser console.
