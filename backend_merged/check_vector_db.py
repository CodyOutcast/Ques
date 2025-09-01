#!/usr/bin/env python3
"""
Vector Database Check Script
Check what data is stored in the vector database
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

try:
    from db_utils import get_vdb_collection, get_user_infos, SessionLocal
    from sqlalchemy import text
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def check_vector_db_content():
    """Check what's stored in the vector database"""
    print("🔍 Checking Vector Database Content...")
    
    try:
        # Get vector database collection
        coll = get_vdb_collection()
        print("✅ Connected to vector database")
        
        # Get collection stats
        try:
            # Try to get some basic info about the collection
            print(f"📊 Collection name: {coll.collection_name}")
            
            # Try to query all documents (with a reasonable limit)
            print("\n🔍 Querying vector database contents...")
            
            # Try to get some sample data
            # Note: Different vector DB implementations may have different query methods
            
            # For Tencent VectorDB, we might need to use a different approach
            # Let's try to query with a dummy vector to see what's stored
            import numpy as np
            
            # Create a dummy query vector (768 dimensions for BGE model)
            dummy_vector = np.random.rand(768).tolist()
            
            # Search with the dummy vector to see what documents exist
            results = coll.search(
                vectors=[dummy_vector],
                limit=100,  # Get up to 100 documents
                retrieve_vector=False,
                output_fields=["text", "id"]  # Try to get text and id fields
            )
            
            print(f"📋 Found {len(results)} result sets")
            
            document_count = 0
            sample_docs = []
            
            for result_set in results:
                for hit in result_set:
                    document_count += 1
                    doc_info = {
                        "id": getattr(hit, 'id', None) or hit.get('id'),
                        "score": getattr(hit, 'score', None) or hit.get('score'),
                    }
                    
                    # Try to get text field if available
                    try:
                        text_content = getattr(hit, 'text', None) or hit.get('text')
                        if text_content:
                            doc_info["text"] = text_content[:100] + "..." if len(text_content) > 100 else text_content
                    except:
                        pass
                    
                    sample_docs.append(doc_info)
                    
                    if len(sample_docs) >= 10:  # Limit to first 10 for display
                        break
                
                if len(sample_docs) >= 10:
                    break
            
            print(f"📊 Total documents found: {document_count}")
            
            if sample_docs:
                print("\n📋 Sample documents:")
                for i, doc in enumerate(sample_docs, 1):
                    print(f"  {i}. ID: {doc['id']}")
                    if 'text' in doc:
                        print(f"      Text: {doc['text']}")
                    if 'score' in doc:
                        print(f"      Score: {doc['score']:.4f}")
                    print()
            else:
                print("📝 No documents found in vector database")
                
        except Exception as e:
            print(f"⚠️ Could not query vector database contents: {e}")
            print("💡 This might be normal if the vector DB implementation doesn't support direct querying")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector database check error: {e}")
        return False

def check_user_vectors_in_postgres():
    """Check which users have vector_id stored in PostgreSQL"""
    print("\n🔍 Checking User Vector IDs in PostgreSQL...")
    
    if not SessionLocal:
        print("❌ Database not available")
        return False
    
    db = SessionLocal()
    try:
        # Check how many users have vector_id
        result = db.execute(text("""
            SELECT 
                COUNT(*) as total_users,
                COUNT(vector_id) as users_with_vectors,
                COUNT(feature_tags) as users_with_tags
            FROM users
        """))
        
        row = result.fetchone()
        if row:
            print(f"📊 Total users: {row[0]}")
            print(f"📊 Users with vector_id: {row[1]}")
            print(f"📊 Users with feature_tags: {row[2]}")
        
        # Get sample of users with vectors
        result = db.execute(text("""
            SELECT user_id, name, vector_id, feature_tags
            FROM users 
            WHERE vector_id IS NOT NULL 
            LIMIT 10
        """))
        
        users_with_vectors = result.fetchall()
        
        if users_with_vectors:
            print(f"\n📋 Sample users with vectors:")
            for user in users_with_vectors:
                try:
                    # Handle both JSON string and list formats
                    if isinstance(user[3], list):
                        tags = user[3]
                    elif isinstance(user[3], str):
                        tags = json.loads(user[3])
                    else:
                        tags = []
                except:
                    tags = []
                print(f"  - User {user[0]} ({user[1]}): vector_id={user[2]}")
                print(f"    Tags: {tags}")
        else:
            print("📝 No users found with vector_id")
        
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL check error: {e}")
        return False
    finally:
        db.close()

def check_environment_variables():
    """Check if vector database environment variables are set"""
    print("\n🔍 Checking Environment Variables...")
    
    required_vars = [
        'VECTORDB_ENDPOINT',
        'VECTORDB_USERNAME', 
        'VECTORDB_KEY',
        'VECTORDB_COLLECTION',
        'VECTORDB_DIMENSION'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Hide sensitive information
            if 'KEY' in var or 'PASSWORD' in var:
                display_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not set")

def main():
    """Run all checks"""
    print("🧪 Vector Database Content Check")
    print("=" * 50)
    
    # Check environment variables
    env_success = check_environment_variables()
    
    # Check PostgreSQL user vectors
    pg_success = check_user_vectors_in_postgres()
    
    # Check vector database content
    vdb_success = check_vector_db_content()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Check Results Summary:")
    print(f"  Environment Variables: {'✅ OK' if env_success else '❌ ISSUES'}")
    print(f"  PostgreSQL Vectors: {'✅ OK' if pg_success else '❌ ISSUES'}")
    print(f"  Vector Database: {'✅ OK' if vdb_success else '❌ ISSUES'}")
    
    overall_success = all([env_success, pg_success, vdb_success])
    print(f"\n🎉 Overall Status: {'✅ ALL CHECKS PASSED' if overall_success else '❌ SOME CHECKS FAILED'}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
