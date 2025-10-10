"""
Configuration management module
"""
import os


class Config:
    """Configuration class"""
    
    def __init__(self):
        # GLM-4 API configuration
        self.glm_api_key = os.getenv('ZHIPUAI_API_KEY') or os.getenv('GLM_API_KEY')
        
        # Qdrant configuration
        self.qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
        self.qdrant_port = int(os.getenv('QDRANT_PORT', '6333'))
        
        # Vector database configuration
        self.collection_name = "users_rawjson"
        
        # Embedding model configuration
        self.dense_model_name = "bge-m3"
        self.sparse_model_name = "splade"
        
        # Search configuration
        self.default_limit = 10
        self.max_candidates = 50
        
        # LLM configuration
        self.default_temperature = 0.3
        self.max_tokens = 1000
    
    def validate(self):
        """Validate configuration"""
        errors = []
        
        if not self.glm_api_key:
            errors.append("GLM API key not set, please set environment variable ZHIPUAI_API_KEY or GLM_API_KEY")
        
        if not self.qdrant_host:
            errors.append("Qdrant host address not set")
        
        if not self.qdrant_port:
            errors.append("Qdrant port not set")
        
        return errors
    
    def __str__(self):
        """Configuration information string representation"""
        return f"""
Config:
  GLM API Key: {'***' + self.glm_api_key[-4:] if self.glm_api_key else 'Not set'}
  Qdrant Host: {self.qdrant_host}
  Qdrant Port: {self.qdrant_port}
  Collection: {self.collection_name}
  Dense Model: {self.dense_model_name}
  Sparse Model: {self.sparse_model_name}
"""