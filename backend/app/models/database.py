import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, JSON, ForeignKey, create_engine, text
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from app.config import settings

Base = declarative_base()

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=True)
    format = Column(String(32), default="txt")
    total_pages = Column(Integer, default=1)
    file_size_bytes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    doc_metadata = Column(JSON, default=dict)

    chunks = relationship("DocumentChunkModel", back_populates="document", cascade="all, delete-orphan")

class DocumentChunkModel(Base):
    __tablename__ = "document_chunks"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(64), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    page_number = Column(Integer, default=1)
    start_char = Column(Integer, default=0)
    end_char = Column(Integer, default=0)
    section_header = Column(String(255), nullable=True)
    token_count = Column(Integer, default=0)
    embedding_json = Column(JSON, nullable=True) # JSON fallback if pgvector extension is not in DB
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("DocumentModel", back_populates="chunks")

class QueryAuditModel(Base):
    __tablename__ = "query_audit_logs"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), nullable=True)
    query_text = Column(Text, nullable=False)
    is_safe = Column(Integer, default=1) # 1 = safe, 0 = flagged
    risk_score = Column(Float, default=0.0)
    generated_answer = Column(Text, nullable=True)
    latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class EvaluationRecordModel(Base):
    __tablename__ = "evaluation_records"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(Text, nullable=False)
    faithfulness = Column(Float, default=0.0)
    context_relevance = Column(Float, default=0.0)
    answer_relevance = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    verdict = Column(String(32), default="PASSED")
    created_at = Column(DateTime, default=datetime.utcnow)

# Database Engine initialization with graceful fallback
def get_engine():
    try:
        if settings.DATABASE_URL and "postgresql" in settings.DATABASE_URL:
            engine = create_engine(
                settings.DATABASE_URL, 
                pool_pre_ping=True, 
                echo=False,
                connect_args={"connect_timeout": 1}
            )
            # Try connection test
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
    except Exception:
        pass
    # Fallback SQLite engine for standalone local testing
    return create_engine("sqlite:///./docintel_local.db", echo=False)

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    # If postgres, try creating pgvector extension and table alterations
    if "postgresql" in str(engine.url):
        try:
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                # Ensure embedding vector column exists
                conn.execute(text(
                    f"ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS embedding vector({settings.VECTOR_DIMENSION});"
                ))
                # Create HNSW Index
                conn.execute(text(
                    f"""
                    CREATE INDEX IF NOT EXISTS idx_chunks_hnsw 
                    ON document_chunks 
                    USING hnsw (embedding vector_cosine_ops)
                    WITH (m = {settings.HNSW_M}, ef_construction = {settings.HNSW_EF_CONSTRUCTION});
                    """
                ))
                conn.commit()
        except Exception as e:
            print(f"PostgreSQL pgvector extension setup note: {e}")
