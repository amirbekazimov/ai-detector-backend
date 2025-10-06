"""Database migration utilities."""

import subprocess
import sys
import os
from app.db.session import engine
from app.db.base import Base


def run_migrations():
    """Run database migrations using Alembic with fallback to manual creation."""
    try:
        # Check if alembic is available
        try:
            subprocess.run([sys.executable, "-c", "import alembic"], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("⚠️ Alembic not available, trying to install...")
            try:
                # Try to install alembic
                subprocess.run([sys.executable, "-m", "pip", "install", "alembic==1.13.1"], 
                             check=True, capture_output=True)
                print("✅ Alembic installed successfully")
            except subprocess.CalledProcessError:
                print("⚠️ Could not install Alembic, using manual table creation...")
                Base.metadata.create_all(bind=engine)
                print("✅ Tables created manually")
                return True
        
        # Change to the backend directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        original_dir = os.getcwd()
        os.chdir(backend_dir)
        
        try:
            # Run alembic upgrade head
            result = subprocess.run([
                sys.executable, "-m", "alembic", "upgrade", "head"
            ], capture_output=True, text=True, check=True)
            
            print("✅ Database migrations completed successfully")
            return True
            
        finally:
            # Always restore original directory
            os.chdir(original_dir)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        # Fallback to creating tables manually
        print("🔄 Falling back to manual table creation...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created manually (fallback)")
        return False
    except Exception as e:
        print(f"❌ Migration error: {e}")
        # Fallback to creating tables manually
        print("🔄 Falling back to manual table creation...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created manually (fallback)")
        return False


def create_tables_manually():
    """Create all tables manually using SQLAlchemy metadata."""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False
