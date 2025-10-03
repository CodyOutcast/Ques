#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vector Embedding Generation and Import Script
Generate BGE-M3 dense vectors and SPLADE sparse vectors based on document design and test dataset
"""

import sqlite3
import json
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from transformers import AutoModelForMaskedLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams, PointStruct
import requests
from datetime import datetime
import re
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
DB_FILE = "quesai_test.db"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "users"

class VectorEmbeddingGenerator:
    def __init__(self):
        """Initialize vector generator"""
        # Initialize Qdrant client, using official recommended connection method
        logger.info("Connecting to Qdrant service...")
        max_retries = 5
        for i in range(max_retries):
            try:
                # Use URL format connection, this is the official recommended method
                self.qdrant_client = QdrantClient(url="http://localhost:6333")
                # Test connection
                collections = self.qdrant_client.get_collections()
                logger.info("Qdrant connection successful")
                logger.info(f"Current collections: {[c.name for c in collections.collections]}")
                break
            except Exception as e:
                logger.warning(f"Qdrant connection attempt {i+1}/{max_retries} failed: {e}")
                if i == max_retries - 1:
                    raise Exception(f"Unable to connect to Qdrant: {e}")
                time.sleep(2)
        
        # Initialize BGE-M3 model (dense vectors)
        logger.info("Loading BGE-M3 model...")
        self.dense_model = SentenceTransformer('BAAI/bge-m3')
        
        # Auto select device (priority mps, cuda, otherwise cpu)
        import torch
        if torch.backends.mps.is_available():
            self.device = 'mps'
        elif torch.cuda.is_available():
            self.device = 'cuda'
        else:
            self.device = 'cpu'
        logger.info(f"Using device: {self.device}")

        # Load SPLADE model, auto fallback on failure
        model_name = "naver/splade-v3"
        try:
            self.sparse_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.sparse_model = AutoModelForMaskedLM.from_pretrained(model_name).to(self.device)
            self.sparse_model.eval()
            logger.info(f"SPLADE model '{model_name}' loaded successfully, device: {self.device}")
        except Exception as e:
            logger.error(f"Failed to load SPLADE-v3: {e}")
            logger.warning("Falling back to naver/splade-cocondenser-ensembledistil")
            model_name = "naver/splade-cocondenser-ensembledistil"
            self.sparse_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.sparse_model = AutoModelForMaskedLM.from_pretrained(model_name).to(self.device)
            self.sparse_model.eval()
            logger.info(f"Fallback model '{model_name}' loaded successfully, device: {self.device}")
        self._torch = torch

        # Database connection
        self.db_conn = None

        logger.info("Vector generator initialization completed")
    
    def create_collection(self):
        """Create Qdrant collection"""
        try:
            # Check if collection already exists
            collections = self.qdrant_client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if COLLECTION_NAME in collection_names:
                logger.info(f"Collection '{COLLECTION_NAME}' already exists, deleting and recreating...")
                self.qdrant_client.delete_collection(COLLECTION_NAME)

            # Create new collection, supporting both dense and sparse vectors
            self.qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config={
                    "dense": VectorParams(
                        size=1024,  # BGE-M3 vector dimension
                        distance=Distance.COSINE
                    )
                },
                sparse_vectors_config={
                    "sparse": {}  # Sparse vector configuration
                }
            )

            logger.info(f"Collection '{COLLECTION_NAME}' created successfully")

        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise
        
    def raw_json_text(user_data):
                return json.dumps(user_data, ensure_ascii=False)
    
    def get_user_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get complete user information from database"""
        try:
            cursor = self.db_conn.cursor()
            
            # Get user basic information and profile
            cursor.execute("""
                SELECT u.id, u.openid, u.name, u.email, u.phone,
                       up.*, 
                       p.name_cn as province_name_cn, p.name_en as province_name_en,
                       c.name_cn as city_name_cn, c.name_en as city_name_en
                FROM users u
                JOIN user_profiles up ON u.id = up.user_id
                LEFT JOIN provinces p ON up.province_id = p.id
                LEFT JOIN cities c ON up.city_id = c.id
                WHERE u.id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            user_data = dict(row)
            
            # Get project information
            cursor.execute("""
                SELECT id, title, description, role, start_date, end_date, 
                       is_current, skills_used, reference_links
                FROM user_projects
                WHERE user_id = ?
                ORDER BY is_current DESC, start_date DESC
            """, (user_id,))
            
            projects = []
            for proj_row in cursor.fetchall():
                proj_data = dict(proj_row)
                proj_data['skills_used'] = self._safe_json_loads(proj_data['skills_used'])
                proj_data['reference_links'] = self._safe_json_loads(proj_data['reference_links'])
                projects.append(proj_data)
            
            # Get institution information
            cursor.execute("""
                SELECT ui.*, i.name as institution_name, i.type as institution_type
                FROM user_institutions ui
                JOIN institutions i ON ui.institution_id = i.id
                WHERE ui.user_id = ?
                ORDER BY ui.is_current DESC, ui.start_date DESC
            """, (user_id,))
            
            institutions = []
            for inst_row in cursor.fetchall():
                inst_data = dict(inst_row)
                institutions.append(inst_data)
            
            # Assemble complete user data
            user_data['projects'] = projects
            user_data['institutions'] = institutions
            
            # Process JSON fields
            json_fields = ['skills', 'hobbies', 'languages', 'resources', 'demands']
            for field in json_fields:
                if field in user_data:
                    user_data[field] = self._safe_json_loads(user_data[field])
            
            return user_data
            
        except Exception as e:
            logger.error(f"Failed to get user data (user_id={user_id}): {e}")
            return None
    
    def _safe_json_loads(self, json_str: str, default=None) -> Any:
        """Safe JSON parsing"""
        if not json_str:
            return default or []
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return default or []
    
    
    def generate_dense_vector(self, text: str) -> List[float]:
        """Generate dense vector"""
        try:
            embedding = self.dense_model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate dense vector: {e}")
            # Return zero vector as fallback
            return [0.0] * 1024
    
    def generate_sparse_vector(self, text: str) -> Dict[int, float]:
        """Generate sparse vector using transformers SPLADE (token_id: weight), auto to(device)"""
        try:
            inputs = self.sparse_tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with self._torch.no_grad():
                outputs = self.sparse_model(**inputs)
                logits = outputs.logits  # [batch, seq_len, vocab_size]
                relu_logits = self._torch.relu(logits)
                splade_scores = self._torch.log1p(relu_logits)
                # max pooling over seq_len
                sparse_vec, _ = splade_scores.max(dim=1)  # [batch, vocab_size]
                sparse_vec = sparse_vec[0]  # Take the first sample
                nonzero_indices = (sparse_vec > 0).nonzero(as_tuple=True)[0]
                indices = nonzero_indices.detach().cpu().tolist()
                values = sparse_vec[nonzero_indices].detach().cpu().tolist()
                sparse_vector = {int(idx): float(val) for idx, val in zip(indices, values)}
            return sparse_vector
        except Exception as e:
            logger.error(f"Failed to generate SPLADE sparse vector: {e}")
            return {}
    
    def build_payload(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build payload structure (based on document design and database fields)"""
        payload = {
            # Basic information
            "user_id": user_data['id'],
            "name": user_data.get('name'),
            "age": user_data.get('age'),
            "gender": user_data.get('gender'),
            
            # Geographic location information
            "province_id": user_data.get('province_id'),
            "city_id": user_data.get('city_id'),
            "province_name_cn": user_data.get('province_name_cn'),
            "city_name_cn": user_data.get('city_name_cn'),
            "province_name_en": user_data.get('province_name_en'),
            "city_name_en": user_data.get('city_name_en'),
            
            # Education information
            "current_university": user_data.get('current_university'),
            "university_verified": user_data.get('university_verified', False),
            
            # Skills and interests
            "skills": user_data.get('skills', []),
            "hobbies": user_data.get('hobbies', []),
            "languages": user_data.get('languages', []),
            "resources": user_data.get('resources', []),
            "demands": user_data.get('demands', []),
            
            # Statistical information
            "project_count": user_data.get('project_count', 0),
            "institution_count": user_data.get('institution_count', 0),
            
            # Status information
            "user_status": "active",  # From users table
            "profile_visibility": user_data.get('profile_visibility', 'public'),
            "is_profile_complete": user_data.get('is_profile_complete', False),
            "wechat_verified": user_data.get('wechat_verified', False),
            
            # Text information (for fuzzy matching)
            "one_sentence_intro": user_data.get('one_sentence_intro'),
            "goals": user_data.get('goals'),
            
            # Project and institution information (simplified version)
            "project_titles": [p.get('title', '') for p in user_data.get('projects', [])],
            "institution_names": [i.get('institution_name', '') for i in user_data.get('institutions', [])],
            "institution_types": [i.get('institution_type', '') for i in user_data.get('institutions', [])],
            
            # Timestamp
            "indexed_at": datetime.now().isoformat()
        }
        
        # Remove None values
        return {k: v for k, v in payload.items() if v is not None}
    
    def process_users(self, batch_size: int = 100, start_user_id: int = 1, max_users: Optional[int] = None):
        """Batch process user data and generate vectors"""
        try:
            self.db_conn = sqlite3.connect(DB_FILE)
            self.db_conn.row_factory = sqlite3.Row
            
            # Get total user count
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            if max_users:
                total_users = min(total_users, max_users)
            
            logger.info(f"Starting vector generation for {total_users} users...")
            
            points = []
            processed_count = 0
            
            for user_id in range(start_user_id, start_user_id + total_users):
                try:
                    # Get user data
                    user_data = self.get_user_data(user_id)
                    if not user_data:
                        continue
                    
                    # Build text
                    dense_text = self.raw_json_text(user_data)
                    sparse_text = self.raw_json_text(user_data)

                    # Generate vectors
                    dense_vector = self.generate_dense_vector(dense_text)
                    sparse_vector = self.generate_sparse_vector(sparse_text)
                    
                    # Build payload
                    payload = self.build_payload(user_data)
                    
                    # Create point
                    point = PointStruct(
                        id=user_id,
                        vector={
                            "dense": dense_vector,
                            "sparse": models.SparseVector(
                                indices=list(sparse_vector.keys()),
                                values=list(sparse_vector.values())
                            )
                        },
                        payload=payload
                    )
                    
                    points.append(point)
                    processed_count += 1
                    
                    # Batch upload
                    if len(points) >= batch_size:
                        self._upload_points(points)
                        points = []
                        logger.info(f"Processed {processed_count}/{total_users} users")
                    
                except Exception as e:
                    logger.error(f"Failed to process user {user_id}: {e}")
                    continue
            
            # Upload remaining points
            if points:
                self._upload_points(points)
            
            logger.info(f"Vector generation completed! Total processed: {processed_count} users")
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise
        finally:
            if self.db_conn:
                self.db_conn.close()
    
    def _upload_points(self, points: List[PointStruct]):
        """Upload points to Qdrant"""
        try:
            self.qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
        except Exception as e:
            logger.error(f"Failed to upload vectors: {e}")
            raise
    
    def get_collection_info(self):
        """Get collection information"""
        try:
            info = self.qdrant_client.get_collection(COLLECTION_NAME)
            return info
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return None

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description="Vector embedding generation and import process")
    parser.add_argument('--collection', type=str, default="users_rawjson", help='Qdrant collection name, default users, optional users_rawjson etc.')
    args = parser.parse_args()

    logger.info("Starting vector embedding generation and import process...")
    try:
        # Initialize generator
        generator = VectorEmbeddingGenerator()

        # Switch collection name (use users_rawjson for raw json)
        global COLLECTION_NAME
        if args.collection == "users_rawjson":
            COLLECTION_NAME = "users_rawjson"

            logger.info("Switched to raw json to text as embedding, collection=users_rawjson")
        else:
            COLLECTION_NAME = "users"

        # Create collection
        generator.create_collection()

        # Process all user data
        generator.process_users(batch_size=50, start_user_id=1, max_users=1000)

        # Get collection information
        collection_info = generator.get_collection_info()
        if collection_info:
            logger.info(f"Collection info: {collection_info}")

        logger.info("Vector embedding generation completed!")
    except Exception as e:
        logger.error(f"Vector generation process failed: {e}")
        raise

if __name__ == "__main__":
    main()