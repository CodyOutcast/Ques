# Migration utilities and helper scripts
import os
import sys
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import db_config
from models import Base

def create_database_if_not_exists(database_name: Optional[str] = None):
    """Create the database if it doesn't exist"""
    db_name = database_name or db_config.PG_DATABASE
    
    # Connect to PostgreSQL server (without specifying database)
    server_url = f"postgresql://{db_config.PG_USER}:{db_config.PG_PASSWORD}@{db_config.PG_HOST}:{db_config.PG_PORT}/postgres"
    engine = create_engine(server_url)
    
    with engine.connect() as conn:
        # Check if database exists
        result = conn.execute(text("SELECT 1 FROM pg_catalog.pg_database WHERE datname = :db_name"), 
                            {"db_name": db_name})
        
        if not result.fetchone():
            # Create database
            conn.execute(text("COMMIT"))  # End any transaction
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
            print(f"✅ Created database: {db_name}")
        else:
            print(f"ℹ️  Database already exists: {db_name}")
    
    engine.dispose()

def run_migrations():
    """Run all Alembic migrations"""
    try:
        # Create database if it doesn't exist
        create_database_if_not_exists()
        
        # Run migrations
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✅ All migrations completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

def create_migration(message: str):
    """Create a new migration file"""
    try:
        alembic_cfg = Config("alembic.ini")
        command.revision(alembic_cfg, message=message, autogenerate=True)
        print(f"✅ Created migration: {message}")
        
    except Exception as e:
        print(f"❌ Failed to create migration: {e}")
        raise

def rollback_migration(revision: str = "-1"):
    """Rollback to a specific migration"""
    try:
        alembic_cfg = Config("alembic.ini")
        command.downgrade(alembic_cfg, revision)
        print(f"✅ Rolled back to: {revision}")
        
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        raise

def check_database_connection():
    """Test database connectivity"""
    try:
        engine = create_engine(db_config.database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful!")
            print(f"🐘 PostgreSQL version: {version}")
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def reset_database():
    """WARNING: Drop all tables and recreate from scratch"""
    try:
        engine = create_engine(db_config.database_url)
        
        # Drop all tables
        Base.metadata.drop_all(engine)
        print("⚠️  Dropped all tables")
        
        # Run migrations
        run_migrations()
        print("✅ Database reset complete!")
        
        engine.dispose()
        
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        raise

def show_migration_status():
    """Show current migration status"""
    try:
        alembic_cfg = Config("alembic.ini")
        command.current(alembic_cfg, verbose=True)
        
    except Exception as e:
        print(f"❌ Failed to show migration status: {e}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration utilities")
    parser.add_argument("action", choices=[
        "migrate", "create", "rollback", "status", "check", "reset"
    ], help="Action to perform")
    parser.add_argument("--message", "-m", help="Migration message (for create)")
    parser.add_argument("--revision", "-r", help="Revision (for rollback)")
    
    args = parser.parse_args()
    
    if args.action == "migrate":
        run_migrations()
    elif args.action == "create":
        if not args.message:
            print("❌ Please provide a migration message with --message")
            sys.exit(1)
        create_migration(args.message)
    elif args.action == "rollback":
        rollback_migration(args.revision or "-1")
    elif args.action == "status":
        show_migration_status()
    elif args.action == "check":
        check_database_connection()
    elif args.action == "reset":
        confirm = input("⚠️  This will DELETE ALL DATA! Type 'YES' to confirm: ")
        if confirm == "YES":
            reset_database()
        else:
            print("❌ Reset cancelled")
    else:
        parser.print_help()
