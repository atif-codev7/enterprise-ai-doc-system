import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic import BaseModel as BaseSettings
    except ImportError:
        BaseSettings = object

class Settings:
    PROJECT_NAME: str = "Enterprise AI Document Intelligence System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Environment & Host
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8002"))
    
    # Database & pgvector
    DATABASE_URL: Optional[str] = os.getenv(
        "DATABASE_URL", 
        "postgresql+psycopg://postgres:postgres@localhost:5432/docintel"
    )
    USE_LOCAL_VECTOR_FALLBACK: bool = os.getenv("USE_LOCAL_VECTOR_FALLBACK", "true").lower() in ("true", "1")
    
    # Vector Search Parameters
    VECTOR_DIMENSION: int = int(os.getenv("VECTOR_DIMENSION", "1536"))
    HNSW_M: int = int(os.getenv("HNSW_M", "16"))
    HNSW_EF_CONSTRUCTION: int = int(os.getenv("HNSW_EF_CONSTRUCTION", "64"))
    HNSW_EF_SEARCH: int = int(os.getenv("HNSW_EF_SEARCH", "40"))
    DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "4"))
    
    # Embeddings & LLM
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "mock")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "deterministic-sim")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", "")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    
    # Chunking Defaults
    DEFAULT_CHUNK_SIZE: int = int(os.getenv("DEFAULT_CHUNK_SIZE", "800"))
    DEFAULT_CHUNK_OVERLAP: int = int(os.getenv("DEFAULT_CHUNK_OVERLAP", "150"))
    
    # Guardrails
    GUARDRAIL_CONFIDENCE_THRESHOLD: float = float(os.getenv("GUARDRAIL_CONFIDENCE_THRESHOLD", "0.75"))
    STRICT_TOOL_VALIDATION: bool = True
    
    # PayGuard Integration
    PAYGUARD_DATABASE_URL: Optional[str] = os.getenv("PAYGUARD_DATABASE_URL", "")

settings = Settings()
