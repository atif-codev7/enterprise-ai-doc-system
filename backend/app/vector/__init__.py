from typing import List, Optional
from app.models.schemas import DocumentChunk, ChunkSearchResult
from app.vector.embeddings import embedding_service
from app.vector.memory_vector_store import MemoryVectorStore
from app.vector.pgvector_store import PgVectorStore
from app.config import settings

class UnifiedVectorStore:
    """
    Unified vector store facade.
    Seamlessly orchestrates PostgreSQL + pgvector HNSW indexing
    and local high-speed in-memory vector indexing.
    """

    def __init__(self):
        self.memory_store = MemoryVectorStore()
        self.pg_store = PgVectorStore()

    def add_chunk(self, chunk: DocumentChunk) -> None:
        if not chunk.embedding:
            chunk.embedding = embedding_service.embed_text(chunk.text)
        
        # Always insert into in-memory store for instant zero-latency retrieval
        self.memory_store.insert_chunk(chunk, chunk.embedding)

        # Also persist to database if available
        self.pg_store.insert_chunk(chunk, chunk.embedding)

    def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        texts = [c.text for c in chunks]
        embeddings = embedding_service.embed_batch(texts)
        for chunk, emb in zip(chunks, embeddings):
            chunk.embedding = emb
            self.memory_store.insert_chunk(chunk, emb)
            self.pg_store.insert_chunk(chunk, emb)

    def search(
        self,
        query: str,
        top_k: int = 4,
        document_id: Optional[str] = None
    ) -> List[ChunkSearchResult]:
        query_vector = embedding_service.embed_text(query)

        # Try pgvector if PostgreSQL is configured and active
        if self.pg_store.is_postgres:
            pg_results = self.pg_store.similarity_search(query_vector, top_k, document_id)
            if pg_results:
                return pg_results

        # Fallback to local memory vector store
        return self.memory_store.similarity_search(query_vector, top_k, document_id)

    def delete_document(self, document_id: str) -> int:
        return self.memory_store.delete_document_chunks(document_id)

    def count(self) -> int:
        return self.memory_store.count()

vector_store = UnifiedVectorStore()

__all__ = ["vector_store", "embedding_service", "UnifiedVectorStore", "MemoryVectorStore", "PgVectorStore"]
