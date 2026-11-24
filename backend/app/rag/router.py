import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from app.models.schemas import (
    DocumentFormat, DocumentUploadResponse, ChatQueryRequest, ChatQueryResponse
)
from app.ingestion.parser import DocumentParser
from app.ingestion.chunker import RecursiveCharacterChunker
from app.vector import vector_store
from app.rag.engine import rag_engine
from app.rag.citation_streamer import stream_rag_tokens
from app.models.database import SessionLocal, DocumentModel

router = APIRouter(prefix="", tags=["RAG & Documents"])

# Store metadata of uploaded documents
_DOCUMENTS_REGISTRY = {}

@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: Optional[UploadFile] = File(None),
    title: Optional[str] = Form(None),
    raw_text: Optional[str] = Form(None),
    doc_format: Optional[str] = Form("txt")
):
    """
    Ingests PDF, Markdown, HTML, or TXT documents, chunks them via RecursiveCharacterChunker,
    generates dense embeddings, and inserts them into pgvector HNSW index.
    """
    doc_id = str(uuid.uuid4())
    doc_title = title or (file.filename if file else "Untitled Document")

    # Determine format
    fmt = DocumentFormat.TXT
    if file:
        ext = file.filename.split(".")[-1].lower() if "." in file.filename else "txt"
        if ext == "pdf":
            fmt = DocumentFormat.PDF
        elif ext in ("md", "markdown"):
            fmt = DocumentFormat.MARKDOWN
        elif ext in ("html", "htm"):
            fmt = DocumentFormat.HTML
        content_bytes = await file.read()
    elif raw_text:
        content_bytes = raw_text.encode("utf-8")
        if doc_format.lower() in [f.value for f in DocumentFormat]:
            fmt = DocumentFormat(doc_format.lower())
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either a file upload or raw_text must be provided."
        )

    # 1. Parse document sections
    sections, meta = DocumentParser.parse(content_bytes, fmt)
    if not sections:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Failed to extract readable text content from document."
        )

    # 2. Chunk with Recursive Character Chunker
    chunker = RecursiveCharacterChunker()
    chunks = chunker.chunk_document_sections(
        document_id=doc_id,
        document_title=doc_title,
        sections=sections
    )

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Chunker produced 0 valid text segments."
        )

    # 3. Embed & Index into pgvector HNSW store
    vector_store.add_chunks(chunks)

    # 4. Save metadata in DB & registry
    total_tokens = sum(c.token_count for c in chunks)
    doc_record = {
        "document_id": doc_id,
        "title": doc_title,
        "format": fmt,
        "chunk_count": len(chunks),
        "total_tokens": total_tokens,
        "total_pages": meta.get("total_pages", 1),
        "created_at": datetime.utcnow()
    }
    _DOCUMENTS_REGISTRY[doc_id] = doc_record

    # Save to persistent database
    db = SessionLocal()
    try:
        db_doc = DocumentModel(
            id=doc_id,
            title=doc_title,
            format=fmt.value,
            total_pages=meta.get("total_pages", 1),
            file_size_bytes=len(content_bytes),
            doc_metadata=meta
        )
        db.add(db_doc)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

    return DocumentUploadResponse(
        document_id=doc_id,
        title=doc_title,
        format=fmt,
        chunk_count=len(chunks),
        total_tokens=total_tokens,
        created_at=doc_record["created_at"],
        message=f"Indexed {len(chunks)} chunks into pgvector HNSW."
    )

@router.get("/documents")
async def list_documents():
    """
    Lists all indexed documents and corpus statistics.
    """
    docs = list(_DOCUMENTS_REGISTRY.values())
    return {
        "total_documents": len(docs),
        "total_indexed_chunks": vector_store.count(),
        "documents": docs
    }

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Deletes document and removes associated vectors from HNSW index.
    """
    deleted_chunks = vector_store.delete_document(document_id)
    if document_id in _DOCUMENTS_REGISTRY:
        del _DOCUMENTS_REGISTRY[document_id]

    db = SessionLocal()
    try:
        db.query(DocumentModel).filter(DocumentModel.id == document_id).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

    return {
        "status": "success",
        "document_id": document_id,
        "deleted_chunks_count": deleted_chunks
    }

@router.post("/rag/chat", response_model=ChatQueryResponse)
async def chat_rag(request: ChatQueryRequest):
    """
    Synchronous full query endpoint returning final answer,
    citations, guardrail check, and tool execution traces.
    """
    return rag_engine.execute_query(request)

@router.post("/rag/chat/stream")
async def chat_rag_stream(request: ChatQueryRequest):
    """
    Token-streaming Server-Sent Events (SSE) endpoint.
    Streams tokens progressively along with inline citations and tool traces.
    """
    return StreamingResponse(
        stream_rag_tokens(
            query=request.message,
            top_k=request.top_k,
            use_tools=request.use_tools,
            temperature=request.temperature
        ),
        media_type="text/event-stream"
    )
