# Development Setup Guide

This guide provides comprehensive instructions for setting up AIAlchemy for local development.

## Table of Contents
- [Quick Start](#quick-start)
- [Detailed Setup Steps](#detailed-setup-steps)
- [Environment Configuration](#environment-configuration)
- [Common Issues & Solutions](#common-issues--solutions)
- [Development Workflow](#development-workflow)
- [Useful Commands](#useful-commands)

## Quick Start

The fastest way to get started with local development:

```bash
# Clone the repository
git clone https://github.com/archetana/AIAlchemy.git
cd AIAlchemy

# Start both servers (recommended)
npm run dev
```

This will start:
- Backend API server on http://localhost:8000
- Frontend React app on http://localhost:3000

[Full content from LOCAL_DEVELOPMENT_SETUP.md...]

## Server Status

To verify your local servers are running correctly:

1. Backend Health Check:
   - Visit http://localhost:8000/health
   - Expected response: `{"status": "healthy"}`

2. Frontend Status:
   - Visit http://localhost:3000
   - Should see the login page

[Content merged from LOCAL_SERVERS_RUNNING.md...]

## Development Best Practices

1. **Always run tests before committing**
2. **Keep both servers running during development**
3. **Watch the logs for errors**
4. **Use separate terminals for backend and frontend**
5. **Clear cache if you see stale data**

[Additional content merged from LOCAL_DEV_STATUS.md...]