# Supabase Database Setup Guide

This guide will help you migrate from SQLite to Supabase PostgreSQL database.

## Prerequisites

1. **Supabase Account**: Sign up at [https://supabase.com](https://supabase.com)
2. **Project Created**: Create a new Supabase project

## Step 1: Create Supabase Project

1. **Login to Supabase Dashboard**
   - Go to [https://supabase.com](https://supabase.com)
   - Sign in with GitHub (recommended) or email

2. **Create New Project**
   - Click "New Project"
   - Choose/create your organization
   - Fill project details:
     - **Name**: `aialchemy-production` (or your choice)
     - **Database Password**: Generate strong password (SAVE THIS!)
     - **Region**: Choose closest to your users
     - **Plan**: Free tier is fine to start

3. **Wait for Setup**: Project creation takes 1-2 minutes

## Step 2: Get Database Connection Info

After project creation, go to **Settings > Database**:

- **Host**: `db.{your-project-id}.supabase.co`
- **Database name**: `postgres`
- **Port**: `5432`
- **User**: `postgres`
- **Password**: The password you set during project creation

Your connection string will look like:
```
postgresql://postgres:{password}@db.{project-id}.supabase.co:5432/postgres
```

**⚠️ Important**: If your password contains special characters (`@`, `:`, `/`, etc.), they must be URL encoded:
- Use the helper script: `python encode_password.py 'your_password' 'project_id'`
- Or manually encode: `@` becomes `%40`, `:` becomes `%3A`, etc.

## Step 3: Run Setup Script

In your backend directory, run the interactive setup:

```bash
cd backend
python setup_supabase.py
```

Follow the prompts to enter your Supabase project details.

## Step 4: Complete Environment Configuration

Edit the generated `.env` file and add these additional keys:

1. **Get API Keys** from Supabase Dashboard > Settings > API:
   ```env
   SUPABASE_ANON_KEY=eyJ...your_anon_key
   SUPABASE_SERVICE_ROLE_KEY=eyJ...your_service_role_key
   ```

2. **Generate Secret Keys**:
   ```bash
   # Generate secret keys
   openssl rand -hex 32  # Copy result to SECRET_KEY
   openssl rand -hex 32  # Copy result to JWT_SECRET_KEY
   ```

   Add to `.env`:
   ```env
   SECRET_KEY=your_generated_secret_key_here
   JWT_SECRET_KEY=your_generated_jwt_secret_key_here
   ```

## Step 5: Run Database Migrations

Create the database schema in Supabase:

```bash
# Test connection first
python setup_supabase.py --test

# Run migrations to create tables
python setup_supabase.py --migrate
```

## Step 6: Migrate Existing Data (Optional)

If you have existing SQLite data to migrate:

```bash
# Export existing data
python export_sqlite_data.py

# Import to Supabase
python import_to_supabase.py
```

## Step 7: Update Application Configuration

1. **Environment Variables**: Ensure `.env` is loaded by your application
2. **Production**: Set these environment variables in your hosting platform
3. **Docker**: Update docker-compose.yml if using containers

## Step 8: Test Everything

1. **Start the application**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. **Check health endpoint**: Visit `http://localhost:8000/health`
3. **Test database operations**: Create a test startup application

## Production Deployment

### Environment Variables for Production

Set these in your production environment (Google Cloud Run, Heroku, etc.):

```env
DATABASE_URL=postgresql+asyncpg://postgres:{password}@db.{project-id}.supabase.co:5432/postgres
SECRET_KEY={your_secret_key}
JWT_SECRET_KEY={your_jwt_secret_key}
SUPABASE_URL=https://{project-id}.supabase.co
SUPABASE_ANON_KEY={your_anon_key}
SUPABASE_SERVICE_ROLE_KEY={your_service_role_key}
ENV=production
DEBUG=false
```

### Supabase Dashboard Features

- **Database**: SQL Editor, Table Editor
- **Authentication**: User management (if using Supabase Auth)
- **Storage**: File storage (alternative to GCS)
- **Edge Functions**: Serverless functions
- **Realtime**: WebSocket subscriptions
- **Monitoring**: Logs and metrics

## Troubleshooting

### Connection Issues
- Verify database password
- Check project ID in connection string
- Ensure network connectivity

### Migration Errors
- Check database permissions
- Verify table constraints
- Review Alembic migration files

### Performance
- Use connection pooling (already configured)
- Add database indexes as needed
- Monitor query performance in Supabase Dashboard

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use service role key** only for server-side operations
3. **Rotate keys regularly** in production
4. **Enable Row Level Security (RLS)** in Supabase for additional protection
5. **Monitor access logs** in Supabase Dashboard

## Next Steps

- **Set up Row Level Security (RLS)** for enhanced security
- **Configure Supabase Auth** if you want to use it instead of JWT
- **Set up database backups** (automatic in Supabase Pro)
- **Monitor database performance** using Supabase Dashboard