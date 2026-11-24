import io
import re
from typing import List, Dict, Any, Tuple
import PyPDF2
from app.models.schemas import DocumentFormat

class DocumentParser:
    """
    Multi-format parser for PDF, Markdown, Plaintext, and HTML documents.
    Extracts text along with page numbers, section headers, and character boundaries.
    """

    @classmethod
    def parse_pdf(cls, file_bytes: bytes) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Parses PDF bytes, yielding page-indexed content blocks.
        """
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        total_pages = len(reader.pages)
        pages_content: List[Dict[str, Any]] = []
        
        metadata = {
            "total_pages": total_pages,
            "pdf_info": {str(k): str(v) for k, v in (reader.metadata or {}).items()}
        }

        char_offset = 0
        for page_idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            # Clean non-printable and excess whitespace
            cleaned_text = re.sub(r"[ \t]+", " ", text).strip()
            if cleaned_text:
                pages_content.append({
                    "page_number": page_idx + 1,
                    "text": cleaned_text,
                    "start_char": char_offset,
                    "end_char": char_offset + len(cleaned_text),
                    "section_header": f"Page {page_idx + 1}"
                })
                char_offset += len(cleaned_text) + 1

        return pages_content, metadata

    @classmethod
    def parse_markdown(cls, text_content: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Parses Markdown string, extracting structured sections based on headers.
        """
        lines = text_content.splitlines()
        sections: List[Dict[str, Any]] = []
        current_header = "Introduction"
        current_lines: List[str] = []
        char_offset = 0
        page_approx = 1

        header_regex = re.compile(r"^(#{1,4})\s+(.+)$")

        for line in lines:
            match = header_regex.match(line.strip())
            if match:
                if current_lines:
                    sec_text = "\n".join(current_lines).strip()
                    if sec_text:
                        sections.append({
                            "page_number": page_approx,
                            "text": sec_text,
                            "start_char": char_offset,
                            "end_char": char_offset + len(sec_text),
                            "section_header": current_header
                        })
                        char_offset += len(sec_text) + 1
                    current_lines = []
                current_header = match.group(2).strip()
                # Rough page approximation: every ~3000 chars advance page
                if char_offset > page_approx * 3000:
                    page_approx += 1
            current_lines.append(line)

        if current_lines:
            sec_text = "\n".join(current_lines).strip()
            if sec_text:
                sections.append({
                    "page_number": page_approx,
                    "text": sec_text,
                    "start_char": char_offset,
                    "end_char": char_offset + len(sec_text),
                    "section_header": current_header
                })

        metadata = {
            "total_pages": page_approx,
            "section_count": len(sections)
        }
        return sections, metadata

    @classmethod
    def parse_html(cls, html_content: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Extracts clean readable text from HTML, removing script and style tags.
        """
        # Strip script and style blocks
        clean = re.sub(r"<script.*?</script>", "", html_content, flags=re.DOTALL | re.IGNORECASE)
        clean = re.sub(r"<style.*?</style>", "", clean, flags=re.DOTALL | re.IGNORECASE)
        # Convert header tags to markdown-like headers for downstream parsing
        clean = re.sub(r"<h[1-6][^>]*>(.*?)</h[1-6]>", r"\n## \1\n", clean, flags=re.IGNORECASE)
        # Convert paragraph breaks
        clean = re.sub(r"</p>", "\n\n", clean, flags=re.IGNORECASE)
        clean = re.sub(r"<br\s*/?>", "\n", clean, flags=re.IGNORECASE)
        # Strip remaining tags
        clean = re.sub(r"<[^>]+>", " ", clean)
        # Unescape and clean whitespaces
        clean = re.sub(r"[ \t]+", " ", clean)
        clean = re.sub(r"\n\s*\n", "\n\n", clean).strip()

        return cls.parse_markdown(clean)

    @classmethod
    def parse(cls, content: bytes, file_format: DocumentFormat) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        if file_format == DocumentFormat.PDF:
            return cls.parse_pdf(content)
        
        text_str = content.decode("utf-8", errors="replace")
        if file_format == DocumentFormat.MARKDOWN:
            return cls.parse_markdown(text_str)
        elif file_format == DocumentFormat.HTML:
            return cls.parse_html(text_str)
        else:
            # Plain text fallback
            return [{
                "page_number": 1,
                "text": text_str.strip(),
                "start_char": 0,
                "end_char": len(text_str.strip()),
                "section_header": "Document"
            }], {"total_pages": max(1, len(text_str) // 3000 + 1)}
