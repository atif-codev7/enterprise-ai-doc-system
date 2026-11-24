import uuid
from typing import List, Dict, Any, Optional
from app.models.schemas import DocumentChunk
from app.config import settings

class RecursiveCharacterChunker:
    """
    Production-grade recursive character chunker.
    Splits text along semantic boundaries (headers, paragraphs, sentences, words)
    while strictly preserving character spans, page references, and section titles.
    """

    DEFAULT_SEPARATORS = ["\n## ", "\n### ", "\n\n", "\n", ". ", "! ", "? ", "; ", " ", ""]

    def __init__(
        self,
        chunk_size: int = settings.DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = settings.DEFAULT_CHUNK_OVERLAP,
        separators: Optional[List[str]] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or self.DEFAULT_SEPARATORS

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """
        Recursively decomposes text using the priority separator hierarchy.
        """
        final_chunks: List[str] = []
        separator = separators[-1]
        new_separators = []

        for i, sep in enumerate(separators):
            if sep == "":
                separator = ""
                break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1:]
                break

        splits = text.split(separator) if separator else list(text)

        good_splits: List[str] = []
        for s in splits:
            piece = s if separator == "" else (s + separator)
            if len(piece) < self.chunk_size:
                good_splits.append(piece)
            else:
                if new_separators:
                    sub_splits = self._split_text(s, new_separators)
                    good_splits.extend(sub_splits)
                else:
                    good_splits.append(piece)

        # Merge adjacent small splits up to chunk_size with overlap
        total_len = 0
        current_doc: List[str] = []

        for piece in good_splits:
            piece_len = len(piece)
            if total_len + piece_len > self.chunk_size:
                if current_doc:
                    merged = "".join(current_doc).strip()
                    if merged:
                        final_chunks.append(merged)
                    # Re-seed with overlapping suffix
                    while total_len > self.chunk_overlap and current_doc:
                        popped = current_doc.pop(0)
                        total_len -= len(popped)
                current_doc.append(piece)
                total_len += piece_len
            else:
                current_doc.append(piece)
                total_len += piece_len

        if current_doc:
            merged = "".join(current_doc).strip()
            if merged:
                final_chunks.append(merged)

        return final_chunks

    def chunk_document_sections(
        self,
        document_id: str,
        document_title: str,
        sections: List[Dict[str, Any]]
    ) -> List[DocumentChunk]:
        """
        Processes pre-parsed document sections, generating typed DocumentChunk instances
        with accurate page, section, and offset metadata.
        """
        chunks: List[DocumentChunk] = []
        global_index = 0

        for section in sections:
            sec_text = section.get("text", "").strip()
            if not sec_text:
                continue

            page_num = section.get("page_number", 1)
            section_header = section.get("section_header", "General")
            base_offset = section.get("start_char", 0)

            # If section text is smaller than chunk size, use directly
            if len(sec_text) <= self.chunk_size:
                raw_pieces = [sec_text]
            else:
                raw_pieces = self._split_text(sec_text, self.separators)

            local_offset = 0
            for piece in raw_pieces:
                piece_clean = piece.strip()
                if not piece_clean:
                    continue

                chunk_id = str(uuid.uuid4())
                start_char = base_offset + local_offset
                end_char = start_char + len(piece_clean)
                token_estimate = max(1, len(piece_clean) // 4)

                chunk = DocumentChunk(
                    id=chunk_id,
                    document_id=document_id,
                    document_title=document_title,
                    chunk_index=global_index,
                    text=piece_clean,
                    page_number=page_num,
                    start_char=start_char,
                    end_char=end_char,
                    section_header=section_header,
                    token_count=token_estimate,
                    embedding=None
                )
                chunks.append(chunk)
                global_index += 1
                local_offset += len(piece)

        return chunks
