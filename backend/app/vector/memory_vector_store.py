from typing import List, Dict, Any, Optional
import numpy as np
from app.models.schemas import DocumentChunk, ChunkSearchResult

class MemoryVectorStore:
    """
    In-memory vector store performing exact / HNSW-equivalent Cosine Similarity search.
    Provides fast, deterministic indexing for local development, tests, and air-gapped environments.
    """

    def __init__(self):
        self._chunks: Dict[str, DocumentChunk] = {}
        self._vectors: Dict[str, np.ndarray] = {}

    def insert_chunk(self, chunk: DocumentChunk, vector: List[float]) -> None:
        self._chunks[chunk.id] = chunk
        arr = np.array(vector, dtype=np.float32)
        norm = np.linalg.norm(arr)
        if norm > 1e-6:
            arr = arr / norm
        self._vectors[chunk.id] = arr

    def insert_batch(self, chunks: List[DocumentChunk], vectors: List[List[float]]) -> None:
        for chunk, vec in zip(chunks, vectors):
            self.insert_chunk(chunk, vec)

    def delete_document_chunks(self, document_id: str) -> int:
        to_delete = [
            cid for cid, chk in self._chunks.items()
            if chk.document_id == document_id
        ]
        for cid in to_delete:
            del self._chunks[cid]
            del self._vectors[cid]
        return len(to_delete)

    def similarity_search(
        self,
        query_vector: List[float],
        top_k: int = 4,
        document_id: Optional[str] = None
    ) -> List[ChunkSearchResult]:
        if not self._chunks or not self._vectors:
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 1e-6:
            q_vec = q_vec / q_norm

        results = []
        for chunk_id, c_vec in self._vectors.items():
            chunk = self._chunks[chunk_id]
            if document_id and chunk.document_id != document_id:
                continue

            # Dot product of unit vectors equals cosine similarity
            similarity = float(np.dot(q_vec, c_vec))
            # Bound to [0.0, 1.0]
            similarity_bounded = max(0.0, min(1.0, (similarity + 1.0) / 2.0))
            results.append((similarity_bounded, chunk))

        # Sort descending by similarity
        results.sort(key=lambda x: x[0], reverse=True)

        ranked_results: List[ChunkSearchResult] = []
        for rank, (score, chunk) in enumerate(results[:top_k], start=1):
            ranked_results.append(
                ChunkSearchResult(
                    chunk=chunk,
                    similarity_score=round(score, 4),
                    rank=rank
                )
            )

        return ranked_results

    def count(self) -> int:
        return len(self._chunks)

    def get_all_chunks(self) -> List[DocumentChunk]:
        return list(self._chunks.values())
