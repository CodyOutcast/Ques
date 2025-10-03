#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Qdrant connection test
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_qdrant_connection():
    """Test Qdrant connection and basic operations"""
    try:
        # Connect according to official documentation
        logger.info("Connecting to Qdrant...")
        client = QdrantClient(url="http://localhost:6333")
        
        # Get collection list
        collections = client.get_collections()
        logger.info(f"Current collections: {[c.name for c in collections.collections]}")
        
        # Create test collection
        test_collection = "test_collection"
        
        # If collection exists, delete it first
        existing_collections = [c.name for c in collections.collections]
        if test_collection in existing_collections:
            logger.info(f"Deleting existing collection: {test_collection}")
            client.delete_collection(test_collection)
        
        # Create new collection
        logger.info("Creating test collection...")
        client.create_collection(
            collection_name=test_collection,
            vectors_config=VectorParams(size=4, distance=Distance.DOT),
        )
        
        # 添加测试向量
        logger.info("添加测试向量...")
        operation_info = client.upsert(
            collection_name=test_collection,
            wait=True,
            points=[
                PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin"}),
                PointStruct(id=2, vector=[0.19, 0.81, 0.75, 0.11], payload={"city": "London"}),
                PointStruct(id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={"city": "Moscow"}),
            ],
        )
        logger.info(f"插入结果: {operation_info}")
        
        # 查询测试
        logger.info("执行查询测试...")
        search_result = client.query_points(
            collection_name=test_collection,
            query=[0.2, 0.1, 0.9, 0.7],
            with_payload=True,
            limit=3
        ).points
        
        logger.info(f"查询结果: {len(search_result)} 个结果")
        for result in search_result:
            logger.info(f"  ID: {result.id}, Score: {result.score}, Payload: {result.payload}")
        
        # 清理测试集合
        logger.info("清理测试集合...")
        client.delete_collection(test_collection)
        
        logger.info("✅ Qdrant连接测试成功！")
        return True
        
    except Exception as e:
        logger.error(f"❌ Qdrant连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_qdrant_connection()