# Quick Local Development Setup

You're absolutely right - testing locally before pushing saves tons of time! Here's the streamlined setup:

## The Problem We Had

The backend has many optional dependencies (Google Cloud, AI/ML packages, etc.) that cause import errors when not installed. For local development, you don't need all of these.

## Simple Solution

### Option 1: Use the Starter Script (Easiest)

**Windows:**
```bash
# Just double-click this file:
start-local-dev.bat
```

**Linux/Mac:**
```bash
chmod +x start-local-dev.sh
./start-local-dev.sh
```

This will:
1. Install minimal dependencies
2. Create `.env` files
3. Start both backend (port 8000) and frontend (port 3000)
4. Open your browser automatically

### Option 2: Manual Setup (If script doesn't work)

#### Backend Setup

```bash
cd backend

# Install ONLY core dependencies (skip ML/AI packages for now)
pip install fastapi uvicorn sqlalchemy aiosqlite pydantic pydantic-settings python-jose passlib bcrypt python-multipart structlog python-dotenv email-validator

# Create minimal .env file
cat > .env << 'EOF'
ENVIRONMENT=development
DATABASE_URL=sqlite+aiosqlite:///./aialchemy_local.db
JWT_SECRET_KEY=local-dev-secret-min-32-chars-long
USE_SUPABASE=false
EOF

# Start backend
python -m uvicorn app.main:app --reload --port 8000
```

If you see errors about missing packages, that's okay! Just install them:
```bash
pip install <package-name>
```

#### Frontend Setup

Open a NEW terminal:

```bash
cd frontend

# Install dependencies (one time)
npm install

# Create .env file
echo "REACT_APP_API_BASE_URL=http://localhost:8000" > .env

# Start frontend
npm start
```

Browser should open at http://localhost:3000

## Testing Registration

1. Go to http://localhost:3000/register
2. Fill in the form with:
   - Email: test@example.com
   - Password: Test123!@#
   - Full Name: Test User
   - Title: Engineer
   - Role: Analyst
3. Click Register
4. ✅ Should be auto-logged in and redirected to dashboard

## Common Issues

### Backend won't start - Module not found

**Solution**: Install the missing package
```bash
cd backend
pip install <missing-package-name>
```

### CORS errors in browser

**Solution**: Make sure backend .env has:
```
CORS_ORIGINS=http://localhost:3000
```

And restart backend server (Ctrl+C then run uvicorn command again)

### Database errors

**Solution**: Delete and recreate database
```bash
cd backend
rm aialchemy_local.db
# Database will be created automatically on next startup
```

### Port already in use

**Backend (8000):**
```bash
# Use different port
python -m uvicorn app.main:app --reload --port 8001

# Then update frontend .env:
echo "REACT_APP_API_BASE_URL=http://localhost:8001" > .env
```

**Frontend (3000):**
```bash
PORT=3001 npm start
```

## Development Workflow

### 1. Make Your Changes

Edit files in your IDE - both backend and frontend will auto-reload!

### 2. Test in Browser

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- Backend health: http://localhost:8000/health

### 3. Check Logs

- **Backend logs**: In the terminal running uvicorn
- **Frontend logs**: In browser console (F12)
- **Network requests**: Browser DevTools > Network tab

### 4. When Everything Works

```bash
git add .
git commit -m "Your message"
git push origin main
```

Only push when local testing is complete!

## Stopping Servers

- **Press Ctrl+C** in each terminal window
- Or just close the terminal windows

## Pro Tips

1. **Keep servers running** while developing - they auto-reload on file changes
2. **Check backend terminal** first if something fails - errors show there
3. **Use browser DevTools** (F12) to see API responses and errors
4. **Test registration thoroughly** before pushing:
   - Valid password
   - Invalid password (should show error)
   - Duplicate email (should show error)
   - Each role type (viewer, analyst, partner, admin)
5. **Clear browser localStorage** if you see auth issues: F12 > Application > Local Storage > Clear

## Minimal Dependencies for Local Dev

If you want the absolute minimum to test registration:

```bash
cd backend
pip install fastapi uvicorn sqlalchemy aiosqlite pydantic pydantic-settings python-jose[cryptography] passlib bcrypt python-multipart structlog python-dotenv email-validator aiofiles
```

That's it! You don't need Google Cloud, AI/ML packages, or any other optional dependencies for basic testing.

## Next Steps After Local Testing Works

1. Test all features locally
2. Make sure registration works perfectly
3. Test different error scenarios
4. Only then: `git push origin main`
5. Check GitHub Actions / deployment logs
6. Test on production

This saves you from multiple deploy cycles! 🚀

## Need Help?

1. Check the terminal output for errors
2. Check browser console (F12) for frontend errors
3. Try http://localhost:8000/docs to test backend API directly
4. Check LOCAL_DEVELOPMENT_SETUP.md for more details

**Remember**: Local development = Fast iteration. Always test locally before pushing!
