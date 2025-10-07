#!/usr/bin/env python3
"""
Supabase Database Setup Script
Helps configure the application to use Supabase PostgreSQL database
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with Supabase configuration"""
    
    print("🚀 Setting up Supabase Database Configuration")
    print("=" * 50)
    
    # Get Supabase project details from user
    print("\n📋 Please provide your Supabase project details:")
    print("   You can find these in your Supabase Dashboard > Settings > Database")
    
    project_url = input("🔗 Project URL (e.g., https://your-project.supabase.co): ").strip()
    if not project_url:
        print("❌ Project URL is required!")
        return False
    
    # Extract project ID from URL
    if "supabase.co" in project_url:
        project_id = project_url.split("https://")[1].split(".supabase.co")[0]
    else:
        project_id = input("🆔 Project ID: ").strip()
    
    db_password = input("🔐 Database Password: ").strip()
    if not db_password:
        print("❌ Database password is required!")
        return False
    
    # Optional: Custom database name (default is postgres)
    db_name = input("🗄️  Database Name (default: postgres): ").strip() or "postgres"
    
    # Build database URL
    database_url = f"postgresql+asyncpg://postgres:{db_password}@db.{project_id}.supabase.co:5432/{db_name}"
    
    # Create .env content
    env_content = f"""# Supabase Database Configuration
DATABASE_URL={database_url}
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Supabase Project Details
SUPABASE_URL={project_url}
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Application Configuration
ENV=development
DEBUG=true
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Security (generate these with: openssl rand -hex 32)
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"""

    # Write .env file
    env_path = Path(".env")
    with open(env_path, "w") as f:
        f.write(env_content)
    
    print(f"\n✅ Created {env_path.absolute()}")
    
    # Show next steps
    print("\n📝 Next Steps:")
    print("1. Update the following in your .env file:")
    print("   - SUPABASE_ANON_KEY (from Supabase Dashboard > Settings > API)")
    print("   - SUPABASE_SERVICE_ROLE_KEY (from Supabase Dashboard > Settings > API)")
    print("   - SECRET_KEY and JWT_SECRET_KEY (generate with: openssl rand -hex 32)")
    print("\n2. Run database migrations:")
    print("   python setup_supabase.py --migrate")
    print("\n3. Test the connection:")
    print("   python setup_supabase.py --test")
    
    return True

def test_connection():
    """Test database connection"""
    import asyncio
    import asyncpg
    
    print("🧪 Testing Supabase Database Connection...")
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    async def test_db():
        try:
            # Parse the asyncpg URL for direct connection test
            url = database_url.replace("postgresql+asyncpg://", "postgresql://")
            conn = await asyncpg.connect(url)
            
            # Test query
            version = await conn.fetchval("SELECT version()")
            print(f"✅ Connected to PostgreSQL: {version[:50]}...")
            
            await conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    return asyncio.run(test_db())

def run_migrations():
    """Run Alembic migrations"""
    print("🔄 Running database migrations...")
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        import subprocess
        
        # Run Alembic migrations
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            print("✅ Migrations completed successfully!")
            print(result.stdout)
        else:
            print("❌ Migration failed:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error running migrations: {e}")

def main():
    """Main setup function"""
    if len(sys.argv) > 1:
        if "--test" in sys.argv:
            test_connection()
        elif "--migrate" in sys.argv:
            run_migrations()
        elif "--help" in sys.argv:
            print("Supabase Setup Script")
            print("Usage:")
            print("  python setup_supabase.py           # Initial setup")
            print("  python setup_supabase.py --test    # Test connection")  
            print("  python setup_supabase.py --migrate # Run migrations")
    else:
        create_env_file()

if __name__ == "__main__":
    main()