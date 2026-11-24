import pytest
import numpy as np
from app.vector.embeddings import embedding_service
from app.vector.memory_vector_store import MemoryVectorStore
from app.models.schemas import DocumentChunk

def test_embedding_normalization():
    text = "PostgreSQL pgvector HNSW indexing with cosine distance."
    vec = embedding_service.embed_text(text)
    assert len(vec) == embedding_service.dimension
    
    # Check L2 unit norm
    norm = np.linalg.norm(np.array(vec))
    assert pytest.approx(norm, rel=1e-3) == 1.0

def test_memory_vector_store_ranking():
    store = MemoryVectorStore()

    chunk1 = DocumentChunk(
        id="chk-1",
        document_id="doc-1",
        document_title="PayGuard Concurrency",
        chunk_index=0,
        text="Row-level locking via with_for_update prevents double spending in PostgreSQL transactions.",
        page_number=1,
        start_char=0,
        end_char=90
    )
    chunk2 = DocumentChunk(
        id="chk-2",
        document_id="doc-2",
        document_title="Gardening Guide",
        chunk_index=0,
        text="Tomatoes require consistent sunlight, organic fertilizer, and well-drained loamy soil.",
        page_number=1,
        start_char=0,
        end_char=88
    )

    store.insert_chunk(chunk1, embedding_service.embed_text(chunk1.text))
    store.insert_chunk(chunk2, embedding_service.embed_text(chunk2.text))

    query = "How do row-level locks prevent race conditions and double spending?"
    q_vec = embedding_service.embed_text(query)

    results = store.similarity_search(q_vec, top_k=2)
    assert len(results) == 2
    # chunk 1 must rank first for a concurrency query
    assert results[0].chunk.id == "chk-1"
    assert results[0].rank == 1
    assert results[0].similarity_score > results[1].similarity_score
