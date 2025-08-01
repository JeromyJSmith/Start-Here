"""
Configuration for Unified Query Service
"""

from typing import List, Dict, Any, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Service configuration"""
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    
    # Service settings
    SERVICE_NAME: str = "unified-query-service"
    SERVICE_PORT: int = 8505
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # API Keys
    LLAMA_INDEX_API_KEY: str = Field(..., description="LlamaIndex API key")
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API key")
    
    # Database connections
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "development"
    REDIS_URL: str = "redis://redis:6379"
    
    # Memory system endpoints
    COGNEE_URL: str = "http://memory-service:8500"
    MEMENTO_URL: str = "http://memory-service:8501"
    MEMOS_URL: str = "http://memos-service:8502"
    LLAMACLOUD_URL: str = "http://llamacloud-service:8504"
    
    # Memory system configuration
    ENABLED_MEMORY_SYSTEMS: List[str] = ["cognee", "memento", "memos", "llamacloud"]
    
    MEMORY_SYSTEM_CONFIG: Dict[str, Dict[str, Any]] = {
        "cognee": {
            "enabled": True,
            "weight": 0.3,
            "timeout": 5.0,
            "max_retries": 3,
            "features": ["semantic_search", "graph_traversal", "concept_linking"]
        },
        "memento": {
            "enabled": True,
            "weight": 0.2,
            "timeout": 3.0,
            "max_retries": 3,
            "features": ["key_value", "fast_retrieval", "simple_storage"]
        },
        "memos": {
            "enabled": True,
            "weight": 0.3,
            "timeout": 5.0,
            "max_retries": 3,
            "features": ["multi_type_memory", "user_context", "activation_memory"]
        },
        "llamacloud": {
            "enabled": True,
            "weight": 0.2,
            "timeout": 10.0,
            "max_retries": 3,
            "features": ["document_search", "structured_extraction", "rag"]
        }
    }
    
    # Document processing configuration
    LLAMAPARSE_CONFIG: Dict[str, Any] = {
        "parsing_instruction": "Extract all content maintaining structure and formatting",
        "result_type": "markdown",
        "num_workers": 4,
        "check_interval": 1,
        "max_timeout": 300,
        "verbose": True
    }
    
    DOCUMENT_PIPELINES: Dict[str, List[str]] = {
        "default": ["parse", "chunk", "embed", "enrich", "store"],
        "fast": ["parse", "chunk", "store"],
        "research": ["parse", "chunk", "embed", "enrich", "citations", "store"],
        "code": ["parse", "syntax_highlight", "dependency_analysis", "store"],
        "legal": ["parse", "clause_extraction", "compliance_check", "store"]
    }
    
    SUPPORTED_FORMATS: List[str] = [
        ".pdf", ".docx", ".txt", ".md", ".html", ".csv", ".xlsx",
        ".pptx", ".json", ".xml", ".py", ".js", ".java", ".cpp"
    ]
    
    # Workflow configuration
    LLAMA_DEPLOY_CONFIG: Dict[str, Any] = {
        "control_plane_port": 8000,
        "service_port_range": [8001, 8010],
        "message_queue": "redis",
        "state_store": "redis",
        "max_workers": 4
    }
    
    WORKFLOW_PORT_RANGE: tuple = (8001, 8010)
    
    ENABLED_WORKFLOWS: List[str] = [
        "memory_sync",
        "document_ingestion", 
        "query_enhancement",
        "maintenance"
    ]
    
    # Caching configuration
    CACHE_CONFIG: Dict[str, Any] = {
        "query_cache": {
            "ttl": 300,  # 5 minutes
            "max_size": 1000
        },
        "document_cache": {
            "ttl": 3600,  # 1 hour
            "max_size": 100
        },
        "embedding_cache": {
            "ttl": 86400,  # 24 hours
            "max_size": 10000
        }
    }
    
    # Performance settings
    MAX_CONCURRENT_QUERIES: int = 50
    QUERY_TIMEOUT: float = 30.0
    BATCH_SIZE: int = 100
    CONNECTION_POOL_SIZE: int = 20
    
    # Ranking configuration
    RANKING_WEIGHTS: Dict[str, float] = {
        "relevance": 0.4,
        "recency": 0.2,
        "source_trust": 0.2,
        "user_preference": 0.2
    }
    
    # Security settings
    API_KEY_HEADER: str = "X-API-Key"
    ENABLE_AUTH: bool = True
    JWT_SECRET: str = Field(..., description="JWT secret for auth")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


# Create settings instance
settings = Settings()