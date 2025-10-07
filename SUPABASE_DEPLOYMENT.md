# 🚀 Supabase Production Deployment Guide

Complete guide for deploying AIAlchemy with Supabase PostgreSQL database in production.

## 📋 Prerequisites

1. **Supabase Project**: Already created at `udjsdlfturbgiqnjsozo.supabase.co`
2. **Database Schema**: Must be executed in Supabase Dashboard
3. **GitHub Secrets**: Required for secure deployment
4. **Google Cloud Project**: For Cloud Run deployment

## 🔐 Step 1: Configure GitHub Repository Secrets

Go to **GitHub Repository** → **Settings** → **Secrets and variables** → **Actions**

Add these secrets:

| Secret Name | Value | Description |
|-------------|--------|-------------|
| `USE_SUPABASE` | `true` | Enable Supabase database backend |
| `SUPABASE_URL` | `https://udjsdlfturbgiqnjsozo.supabase.co` | Supabase project URL |
| `SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Supabase anonymous key |

### Additional Required Secrets (if not already set):
```bash
SECRET_KEY=your_production_secret_key_here
JWT_SECRET_KEY=your_production_jwt_secret_key_here
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
GCS_BUCKET_NAME=your_bucket_name
GCS_SERVICE_ACCOUNT_KEY={"type":"service_account",...}
```

## 🗄️ Step 2: Execute Database Schema in Supabase

**CRITICAL**: This step must be completed before deployment!

### Manual Schema Execution:
1. **Go to**: https://supabase.com/dashboard
2. **Open project**: `udjsdlfturbgiqnjsozo`
3. **Navigate to**: SQL Editor
4. **Copy contents** of `backend/supabase_schema.sql`
5. **Paste and click**: "Run" to execute

### What the schema creates:
- ✅ **8 Tables**: industries, users, startup_applications, founders, uploaded_files, etc.
- ✅ **3 Enums**: application_status, funding_stage, file_status  
- ✅ **Indexes**: Performance optimization for queries
- ✅ **Triggers**: Auto-update timestamps
- ✅ **RLS Policies**: Row Level Security configuration
- ✅ **Default Data**: Industries and investment weights

### Verify Schema Execution:
```bash
# Test locally after schema execution
cd backend
python simple_supabase_test.py
```

## 🚀 Step 3: Deploy to Production

### Automatic Deployment (Recommended):
```bash
# Push to main branch triggers deployment
git push origin main
```

### Manual Deployment:
```bash
# Or trigger manually via GitHub Actions
# Go to Actions → Deploy to Production → Run workflow
```

## 🔧 Step 4: Environment Configuration

The deployment uses these environment variables in Cloud Run:

```bash
# Database Configuration
USE_SUPABASE=true
SUPABASE_URL=https://udjsdlfturbgiqnjsozo.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...

# Hybrid Database Support
DATABASE_URL=sqlite+aiosqlite://./aialchemy.db  # Fallback

# Application Settings
ENVIRONMENT=production
DEBUG=false

# Google Cloud Integration
USE_GOOGLE_CLOUD_STORAGE=true
GOOGLE_CLOUD_STORAGE_BUCKET=your_bucket_name
```

## ✅ Step 5: Verify Deployment

After successful deployment:

### 1. Check Service Health:
```bash
curl https://your-backend-url.run.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "aialchemy-backend", 
  "database": "connected",
  "tables_initialized": true
}
```

### 2. Test Database Operations:
```bash
# Test startup creation
curl -X POST https://your-backend-url.run.app/api/startups/ \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Company",
    "contact_email": "test@example.com",
    "contact_name": "Test User",
    "funding_stage": "seed"
  }'
```

### 3. Verify Supabase Integration:
- Go to Supabase Dashboard → Table Editor
- Check `startup_applications` table for new records
- Verify data is properly stored and formatted

## 🔄 Step 6: Database Migration (Optional)

If you have existing SQLite data to migrate:

### 1. Export SQLite Data:
```bash
cd backend
python migrate_sqlite_to_supabase.py
```

### 2. Verify Migration:
```bash
python verify_supabase_setup.py
```

## 🏗️ Architecture Overview

### Production Architecture:
```
Internet
    ↓
Google Cloud Load Balancer
    ↓
nginx-gateway (Cloud Run)
    ↓
├── Frontend (Cloud Run) → Static React App
└── Backend (Cloud Run) → FastAPI + Supabase
    ↓
├── Supabase PostgreSQL → Primary Database
├── Google Cloud Storage → File Storage
└── SQLite → Development Fallback
```

### Database Hybrid Architecture:
```python
# The application automatically chooses:
if USE_SUPABASE=true:
    → Supabase PostgreSQL (Production)
else:
    → SQLite (Development)
```

## 🛠️ Troubleshooting

### Common Issues:

#### 1. Database Connection Errors:
```bash
# Check environment variables
echo $SUPABASE_URL
echo $USE_SUPABASE

# Test connection
python simple_supabase_test.py
```

#### 2. Schema Not Found Errors:
```
Error: "Could not find the table 'startup_applications'"
```
**Solution**: Execute schema in Supabase Dashboard (Step 2)

#### 3. IPv6 Network Errors:
```
Error: "Network is unreachable"  
```
**Solution**: Already fixed with IPv4-only configuration

#### 4. Authentication Errors:
```
Error: "Invalid API key"
```
**Solution**: Verify `SUPABASE_ANON_KEY` in GitHub secrets

## 📊 Monitoring & Maintenance

### Health Checks:
- **Endpoint**: `/health`
- **Frequency**: Every 30 seconds
- **Alerts**: Set up in Google Cloud Monitoring

### Database Monitoring:
- **Supabase Dashboard**: Real-time metrics
- **Connection Pool**: Monitor active connections
- **Query Performance**: Check slow queries

### Log Monitoring:
```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Filter for database errors
gcloud logging read "resource.type=cloud_run_revision AND textPayload:database" --limit 10
```

## 🎯 Production Checklist

Before going live:

- [ ] ✅ Schema executed in Supabase
- [ ] ✅ GitHub secrets configured
- [ ] ✅ Deployment successful
- [ ] ✅ Health checks passing
- [ ] ✅ Database connection verified
- [ ] ✅ File uploads working
- [ ] ✅ API endpoints accessible
- [ ] ✅ Frontend connecting to backend
- [ ] ✅ SSL certificates valid
- [ ] ✅ Monitoring configured

## 🔗 Useful Links

- **Supabase Dashboard**: https://supabase.com/dashboard
- **GitHub Actions**: https://github.com/archetana/AIAlchemy/actions
- **Google Cloud Console**: https://console.cloud.google.com
- **Cloud Run Services**: https://console.cloud.google.com/run

---

**🎉 You're now ready for production with Supabase!**

The hybrid database architecture ensures you can develop locally with SQLite and deploy to production with Supabase PostgreSQL seamlessly.