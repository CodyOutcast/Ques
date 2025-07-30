#!/usr/bin/env python3
"""
Create VectorDB Collection with Proper Configuration (from backend_p12)
"""

import os
from tcvectordb import VectorDBClient
from tcvectordb.model.enum import FieldType, IndexType, MetricType, EmbeddingModel
from tcvectordb.model.index import Index, FilterIndex, VectorIndex, HNSWParams
from tcvectordb.model.collection import Embedding
from tcvectordb.model.document import Document
import tcvectordb.exceptions
import time

def create_vectordb_collection():
    """Create VectorDB collection with proper configuration"""
    print("🚀 Creating VectorDB Collection")
    print("=" * 50)
    
    # Configuration from backend_p12
    vdb_url = "http://gz-vdb-ccj83iw2.sql.tencentcdb.com:8100"
    vdb_username = "root"
    vdb_key = "56Nw7FeOPhlUF0E7F8BtveusjnzlG3DEMCyOFyRm"
    db_name = "startup_db"
    collection_name = "user_vectors"
    
    try:
        # Create client
        client = VectorDBClient(url=vdb_url, username=vdb_username, key=vdb_key, timeout=30)
        print(f"✅ Connected to VectorDB")
        
        # Get or create database
        try:
            db = client.database(db_name)
            print(f"✅ Connected to existing database: {db_name}")
        except tcvectordb.exceptions.VectorDBException:
            db = client.create_database(db_name)
            print(f"✅ Created new database: {db_name}")
        
        # Check if collection exists
        try:
            collection = db.collection(collection_name)
            print(f"⚠️  Collection '{collection_name}' already exists")
            print(f"✅ Using existing collection")
        except tcvectordb.exceptions.VectorDBException:
            print(f"🔧 Creating collection: {collection_name}")
            
            # Create collection with proper configuration
            # Use BGE_BASE_ZH embeddings (Chinese BERT)
            embedding = Embedding(
                vector_field="vector",
                field="text", 
                model=EmbeddingModel.BGE_BASE_ZH
            )
            
            # Get dimension with default
            dimension = int(os.getenv('VECTORDB_DIMENSION', '768'))
            
            # Create index for vector search using correct API
            index = Index(
                FilterIndex("id", FieldType.String, IndexType.PRIMARY_KEY),
                VectorIndex(
                    "vector",
                    dimension,
                    IndexType.HNSW,
                    MetricType.COSINE,
                    HNSWParams(m=16, efconstruction=200)
                )
            )
            
            # Create collection with proper replica configuration
            collection = db.create_collection(
                name=collection_name,
                shard=1,  # Basic setup; increase for production
                replicas=1,  # Fixed: must be between 1 and 29
                description="User preference vectors for recommendation system",
                index=index,
                embedding=embedding
            )
            print(f"✅ Collection '{collection_name}' created successfully")
        
        # Test collection operations
        print(f"\n🧪 Testing Collection Operations")
        print("-" * 30)
        
        # Test inserting a sample document
        test_doc = Document(
            id="test_999",
            text="测试用户偏好数据：喜欢技术、创业、人工智能"  # Test user preference data in Chinese
        )
        
        print(f"\n📝 Testing document insertion...")
        result = collection.upsert([test_doc])
        print(f"✅ Document inserted: {result}")
        
        # Wait a moment for indexing
        time.sleep(3)
        
        # Test querying by ID
        print(f"\n🔍 Testing document query...")
        query_result = collection.query(
            document_ids=["test_999"],
            limit=1,
            retrieve_vector=False
        )
        print(f"✅ Query result: {len(query_result)} documents found")
        if query_result:
            print(f"   Document ID: {query_result[0].get('id', 'N/A')}")
            print(f"   Document text: {query_result[0].get('text', 'N/A')}")
        
        # Clean up test document
        collection.delete(document_ids=["test_999"])
        print(f"🧹 Test document cleaned up")
        
        print(f"\n✅ VectorDB collection '{collection_name}' is ready for use!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        import traceback
        print(f"🔍 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_vectordb_collection()
