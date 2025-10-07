#!/usr/bin/env python3
"""
SQLite to Supabase Migration Script
Migrates existing data from SQLite to Supabase PostgreSQL
"""

import asyncio
import json
import os
from pathlib import Path
from typing import List, Dict, Any

import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

def export_sqlite_data():
    """Export data from SQLite database"""
    print("📤 Exporting data from SQLite...")
    
    # Connect to SQLite
    sqlite_engine = create_engine('sqlite:///aialchemy.db')
    Session = sessionmaker(bind=sqlite_engine)
    session = Session()
    
    data = {}
    
    try:
        # Export tables in dependency order
        tables = [
            'users',
            'industries', 
            'startup_applications',
            'founders',
            'uploaded_files',
            'financial_metrics',
            'investment_memos',
            'evaluation_history',
            'pipeline_metrics',
            'investment_weights'
        ]
        
        for table in tables:
            try:
                result = session.execute(text(f"SELECT * FROM {table}"))
                rows = [dict(row._mapping) for row in result]
                data[table] = rows
                print(f"  ✓ Exported {len(rows)} records from {table}")
            except Exception as e:
                print(f"  ⚠️  Could not export {table}: {e}")
                data[table] = []
        
        # Save to JSON file
        with open('sqlite_export.json', 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"✅ Data exported to sqlite_export.json")
        return data
        
    finally:
        session.close()

async def import_to_supabase(data: Dict[str, List[Dict]]):
    """Import data to Supabase PostgreSQL"""
    print("📥 Importing data to Supabase...")
    
    # Load environment
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found. Make sure to run setup_supabase.py first.")
        return False
    
    # Convert asyncpg URL
    url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    conn = await asyncpg.connect(url)
    
    try:
        # Import tables in dependency order
        table_order = [
            'users',
            'industries',
            'startup_applications', 
            'founders',
            'uploaded_files',
            'financial_metrics',
            'investment_memos',
            'evaluation_history',
            'pipeline_metrics',
            'investment_weights'
        ]
        
        for table in table_order:
            if table not in data or not data[table]:
                print(f"  ⏭️  Skipping {table} (no data)")
                continue
            
            rows = data[table]
            
            if not rows:
                continue
                
            # Get column names from first row
            columns = list(rows[0].keys())
            
            # Create placeholders for INSERT
            placeholders = ', '.join([f'${i+1}' for i in range(len(columns))])
            columns_str = ', '.join(columns)
            
            insert_sql = f"""
                INSERT INTO {table} ({columns_str}) 
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING
            """
            
            # Insert each row
            inserted = 0
            for row in rows:
                try:
                    values = [row[col] for col in columns]
                    await conn.execute(insert_sql, *values)
                    inserted += 1
                except Exception as e:
                    print(f"    ⚠️  Error inserting row in {table}: {e}")
            
            print(f"  ✓ Imported {inserted}/{len(rows)} records to {table}")
        
        print("✅ Data import completed!")
        return True
        
    finally:
        await conn.close()

async def verify_migration():
    """Verify that migration was successful"""
    print("🔍 Verifying migration...")
    
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    conn = await asyncpg.connect(url)
    
    try:
        tables = [
            'users', 'industries', 'startup_applications', 'founders',
            'uploaded_files', 'financial_metrics'
        ]
        
        for table in tables:
            try:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                print(f"  {table}: {count} records")
            except Exception as e:
                print(f"  {table}: Error - {e}")
        
    finally:
        await conn.close()

def main():
    """Main migration function"""
    import sys
    
    if len(sys.argv) > 1:
        if "--export" in sys.argv:
            export_sqlite_data()
        elif "--import" in sys.argv:
            # Load exported data
            if not Path('sqlite_export.json').exists():
                print("❌ sqlite_export.json not found. Run with --export first.")
                return
            
            with open('sqlite_export.json', 'r') as f:
                data = json.load(f)
            
            asyncio.run(import_to_supabase(data))
        elif "--verify" in sys.argv:
            asyncio.run(verify_migration())
        elif "--all" in sys.argv:
            # Full migration
            data = export_sqlite_data()
            asyncio.run(import_to_supabase(data))
            asyncio.run(verify_migration())
    else:
        print("SQLite to Supabase Migration Tool")
        print("Usage:")
        print("  python migrate_sqlite_to_supabase.py --export   # Export SQLite data")
        print("  python migrate_sqlite_to_supabase.py --import   # Import to Supabase") 
        print("  python migrate_sqlite_to_supabase.py --verify   # Verify migration")
        print("  python migrate_sqlite_to_supabase.py --all      # Full migration")

if __name__ == "__main__":
    main()