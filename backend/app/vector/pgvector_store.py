import json
from typing import List, Optional
from sqlalchemy import text
from app.config import settings
from app.models.database import SessionLocal, DocumentChunkModel, engine
from app.models.schemas import DocumentChunk, ChunkSearchResult

class PgVectorStore:
    """
    PostgreSQL + pgvector storage and HNSW retrieval engine.
    Uses vector_cosine_ops with configurable m and ef_construction parameters.
    """

    def __init__(self):
        self.is_postgres = "postgresql" in str(engine.url)

    def insert_chunk(self, chunk: DocumentChunk, vector: List[float]) -> bool:
        db = SessionLocal()
        try:
            db_chunk = DocumentChunkModel(
                id=chunk.id,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                page_number=chunk.page_number,
                start_char=chunk.start_char,
                end_char=chunk.end_char,
                section_header=chunk.section_header,
                token_count=chunk.token_count,
                embedding_json=vector
            )
            db.add(db_chunk)
            db.commit()

            if self.is_postgres:
                # Update pgvector native vector column
                vec_str = "[" + ",".join(str(x) for x in vector) + "]"
                db.execute(
                    text("UPDATE document_chunks SET embedding = :vec::vector WHERE id = :cid"),
                    {"vec": vec_str, "cid": chunk.id}
                )
                db.commit()
            return True
        except Exception as e:
            db.rollback()
            return False
        finally:
            db.close()

    def similarity_search(
        self,
        query_vector: List[float],
        top_k: int = 4,
        document_id: Optional[str] = None
    ) -> List[ChunkSearchResult]:
        if not self.is_postgres:
            return []

        db = SessionLocal()
        try:
            # Set HNSW ef_search dynamically for this session query
            db.execute(text(f"SET LOCAL hnsw.ef_search = {settings.HNSW_EF_SEARCH};"))

            vec_str = "[" + ",".join(str(x) for x in query_vector) + "]"
            
            filter_clause = "WHERE document_id = :doc_id" if document_id else ""
            sql = f"""
                SELECT 
                    id, document_id, chunk_index, text, page_number, 
                    start_char, end_char, section_header, token_count,
                    1 - (embedding <=> :query_vec::vector) AS cosine_similarity
                FROM document_chunks
                {filter_clause}
                ORDER BY embedding <=> :query_vec::vector
                LIMIT :top_k;
            """
            
            params = {"query_vec": vec_str, "top_k": top_k}
            if document_id:
                params["doc_id"] = document_id

            rows = db.execute(text(sql), params).fetchall()
            results = []

            for rank, r in enumerate(rows, start=1):
                chunk = DocumentChunk(
                    id=r[0],
                    document_id=r[1],
                    document_title="Document",
                    chunk_index=r[2],
                    text=r[3],
                    page_number=r[4],
                    start_char=r[5],
                    end_char=r[6],
                    section_header=r[7],
                    token_count=r[8]
                )
                similarity = float(r[9]) if r[9] is not None else 0.0
                results.append(
                    ChunkSearchResult(
                        chunk=chunk,
                        similarity_score=round(max(0.0, min(1.0, similarity)), 4),
                        rank=rank
                    )
                )

            return results
        except Exception:
            return []
        finally:
            db.close()
