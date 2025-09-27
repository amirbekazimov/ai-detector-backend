#!/usr/bin/env python3
"""
Migration script to add 'name' field to existing sites table.
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def migrate_add_site_name():
    """Add name field to existing sites table."""
    
    print("Starting migration: Add site name field...")
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        with engine.connect() as conn:
            # Check if name column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='sites' AND column_name='name'
            """))
            
            if result.fetchone():
                print("✅ Column 'name' already exists. Migration not needed.")
                return
        
        # Add the name column with default empty string
        print("Adding 'name' column to sites table...")
        with engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE sites 
                ADD COLUMN name VARCHAR NOT NULL DEFAULT ''
            """))
            conn.commit()
        
        print("✅ Successfully added 'name' column")
        
        # Update existing sites to use domain as name if name is empty
        print("Updating existing sites...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                UPDATE sites 
                SET name = domain 
                WHERE name = '' OR name IS NULL
            """))
            conn.commit()
            
            print(f"✅ Updated {result.rowcount} existing sites")
        
        print("🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == "__main__":
    migrate_add_site_name()
