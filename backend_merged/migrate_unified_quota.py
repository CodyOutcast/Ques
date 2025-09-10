"""
Database migration to add monthly tracking to UserUsageLog
Run this script to add the month_timestamp column for unified quota system
"""

from sqlalchemy import text
from dependencies.db import engine
import logging

logger = logging.getLogger(__name__)

def add_month_timestamp_column():
    """Add month_timestamp column to user_usage_logs table"""
    try:
        with engine.connect() as connection:
            # Check if column already exists
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user_usage_logs' 
                AND column_name = 'month_timestamp'
            """))
            
            if result.fetchone():
                print("✅ month_timestamp column already exists")
                return True
            
            # Add the column
            connection.execute(text("""
                ALTER TABLE user_usage_logs 
                ADD COLUMN month_timestamp TIMESTAMP
            """))
            
            # Update existing records with month_timestamp
            connection.execute(text("""
                UPDATE user_usage_logs 
                SET month_timestamp = DATE_TRUNC('month', day_timestamp)
                WHERE month_timestamp IS NULL
            """))
            
            # Make the column NOT NULL after populating it
            connection.execute(text("""
                ALTER TABLE user_usage_logs 
                ALTER COLUMN month_timestamp SET NOT NULL
            """))
            
            connection.commit()
            print("✅ Successfully added month_timestamp column and populated existing data")
            return True
            
    except Exception as e:
        logger.error(f"Error adding month_timestamp column: {e}")
        print(f"❌ Failed to add month_timestamp column: {e}")
        return False

def migrate_quota_data():
    """Migrate any existing quota data from old system (if present)"""
    try:
        with engine.connect() as connection:
            # Check if old quota tables exist
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'user_subscriptions'
            """))
            
            if not result.fetchone():
                print("ℹ️ No old quota tables found, skipping migration")
                return True
            
            # Migrate subscription data to membership if needed
            # This is optional - we're keeping the membership system as primary
            print("ℹ️ Old quota tables found but keeping membership system as primary")
            print("ℹ️ You may want to manually review and migrate any important data")
            
            return True
            
    except Exception as e:
        logger.error(f"Error migrating quota data: {e}")
        print(f"❌ Failed to migrate quota data: {e}")
        return False

def run_migration():
    """Run the complete migration"""
    print("🚀 Starting unified quota system migration...")
    print("=" * 50)
    
    # Step 1: Add month_timestamp column
    print("Step 1: Adding month_timestamp column to user_usage_logs...")
    if not add_month_timestamp_column():
        return False
    
    # Step 2: Migrate old quota data (optional)
    print("\nStep 2: Checking for old quota data migration...")
    if not migrate_quota_data():
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Migration completed successfully!")
    print("\nUnified quota system is now active with:")
    print("- Daily limits for spam prevention")
    print("- Monthly quotas for cost control") 
    print("- Hourly rate limits for abuse prevention")
    print("- Single membership system managing all limits")
    
    return True

if __name__ == "__main__":
    run_migration()
