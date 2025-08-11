#!/bin/bash
# Create the missing migration file directly on server

echo "Creating 008_message_search_indexes.py migration file..."

cat > /opt/ques-backend/migrations/versions/008_message_search_indexes.py << 'EOF'
"""Add message search indexes

Revision ID: 008_message_search_indexes
Revises: 007_project_status
Create Date: 2025-08-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008_message_search_indexes'
down_revision = '007_project_status'
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes for message search functionality"""
    
    # Add basic indexes that work across different database systems
    try:
        # Basic case-insensitive index for LIKE queries (works on most databases)
        op.create_index(
            'idx_messages_text_lower',
            'messages',
            [sa.text('LOWER(text)')]
        )
        print("✅ Added case-insensitive text search index")
    except Exception as e:
        print(f"⚠️  Text index creation failed: {e}")
    
    # Add composite index for match_id + timestamp (for conversation search)
    try:
        op.create_index(
            'idx_messages_match_timestamp',
            'messages',
            ['match_id', 'timestamp']
        )
        print("✅ Added match-timestamp composite index")
    except Exception as e:
        print(f"⚠️  Match-timestamp index creation failed: {e}")
    
    # Add index for sender_id (for user-specific searches)
    try:
        op.create_index(
            'idx_messages_sender_timestamp',
            'messages',
            ['sender_id', 'timestamp']
        )
        print("✅ Added sender-timestamp composite index")
    except Exception as e:
        print(f"⚠️  Sender-timestamp index creation failed: {e}")
    
    print("✅ Message search indexes setup completed")


def downgrade():
    """Remove message search indexes"""
    
    # Remove the indexes
    try:
        op.drop_index('idx_messages_match_timestamp', table_name='messages')
        op.drop_index('idx_messages_sender_timestamp', table_name='messages')
        op.drop_index('idx_messages_text_lower', table_name='messages')
        print("✅ Removed message search indexes")
    except Exception as e:
        print(f"⚠️  Error removing some indexes: {e}")
EOF

echo "✅ Migration file created!"
echo "Now run: alembic upgrade head"
