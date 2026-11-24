import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.rag.router import router as rag_router
from app.evaluation.router import router as eval_router
from app.models.database import init_db
from app.ingestion.parser import DocumentParser
from app.ingestion.chunker import RecursiveCharacterChunker
from app.vector import vector_store
from app.models.schemas import DocumentFormat

# Seed Architecture Document on startup
INITIAL_SPEC_MARKDOWN = """# Flagship Architectural Portfolio Specifications

## PayGuard: High-Concurrency Financial Ledger System
PayGuard is a high-concurrency financial ledger engine engineered in FastAPI, PostgreSQL, and Redis.
Core focus areas are data integrity, race-condition elimination, and transaction isolation.
Key architectural features include:
1. Double-Entry Bookkeeping Schema: Every financial transaction creates paired debit and credit entries. Every debit has an offsetting credit of equal value, ensuring mathematical reconciliation.
2. Idempotent Transfers: Clients generate unique idempotency keys (e.g., idemp-sec-tx-89210-apex) tracked in Redis cache and PostgreSQL to prevent duplicate billing.
3. Row-Level Locking: Utilizes SELECT with_for_update() row locks during balance updates, completely preventing race conditions and double-spending across concurrent parallel threads.
4. Concurrency Verification: Includes an automated 50-request parallel Pytest concurrency test suite.

## Reliable Webhook and Asynchronous Job Engine
The Webhook Engine delivers fault-tolerant, at-least-once asynchronous task execution:
1. High-throughput producer returning HTTP 202 Accepted immediately to decoupled callers.
2. ARQ async worker fleet operating with exponential backoff schedules (1s, 2s, 4s, 8s, 16s).
3. Dead Letter Queue (DLQ) isolation with administrative manual retry triggers.
4. Kill -9 Recovery Proof: Workers can be terminated mid-execution without dropping tasks or creating zombie database states.

## Enterprise AI Document Intelligence System
The Document Intelligence System orchestrates production applied AI with RAG optimization and deterministic state workflows:
1. Multi-format Ingestion: Supports PDF, Markdown, HTML, and text via recursive character chunking with section and page preservation.
2. Semantic Vector Search: pgvector HNSW indexing using vector_cosine_ops with m=16, ef_construction=64, and dynamic ef_search=40.
3. Token-streaming RAG Interface: Real-time Server-Sent Events (SSE) token delivery with verified inline citation markers linking directly to source passages.
4. LangGraph Deterministic Workflows: State graph routing between prompt-injection guardrails, vector retrieval, and PayGuard ledger inspection tools.
5. Quantitative Ragas Evaluation: Automated benchmark suite scoring Faithfulness, Context Relevance, and Answer Relevance.
6. Guardrails: Regex heuristics and semantic analysis blocking prompt injections, jailbreaks, and parameter tampering.
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema
    init_db()

    # Seed initial architecture knowledge document if corpus is empty
    if vector_store.count() == 0:
        doc_id = "doc-arch-portfolio-spec"
        doc_title = "Flagship Architectural Portfolio Specifications"
        sections, meta = DocumentParser.parse(INITIAL_SPEC_MARKDOWN.encode("utf-8"), DocumentFormat.MARKDOWN)
        chunker = RecursiveCharacterChunker(chunk_size=600, chunk_overlap=100)
        chunks = chunker.chunk_document_sections(doc_id, doc_title, sections)
        vector_store.add_chunks(chunks)
        print(f"[DocIntel] Seeded {len(chunks)} chunks from architecture portfolio specification.")

    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise AI Document Intelligence System with pgvector HNSW, LangGraph, Guardrails & Ragas Evaluation",
    lifespan=lifespan
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(rag_router, prefix=settings.API_V1_STR)
app.include_router(eval_router, prefix=settings.API_V1_STR)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
        "vector_store_chunks": vector_store.count(),
        "database_backend": "PostgreSQL + pgvector" if vector_store.pg_store.is_postgres else "Local High-Performance Vector Store",
        "guardrail_engine": "Active (Prompt Injection & Pydantic Validation)",
        "ragas_evaluation": "Enabled"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
