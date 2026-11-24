import pytest
from app.ingestion.parser import DocumentParser
from app.ingestion.chunker import RecursiveCharacterChunker
from app.models.schemas import DocumentFormat

def test_markdown_parser():
    md = """# Title of Doc
Introduction to ledger system.

## Architectural Model
The ledger implements ACID transactions.

### Consistency Rules
Debits must match credits."""
    
    sections, meta = DocumentParser.parse_markdown(md)
    assert len(sections) >= 3
    assert meta["section_count"] >= 3
    headers = [s["section_header"] for s in sections]
    assert "Architectural Model" in headers or "Consistency Rules" in headers

def test_recursive_chunker_basic():
    text = "Sentence one about PayGuard. " * 30
    sections = [{
        "page_number": 1,
        "text": text,
        "start_char": 0,
        "end_char": len(text),
        "section_header": "Overview"
    }]

    chunker = RecursiveCharacterChunker(chunk_size=200, chunk_overlap=50)
    chunks = chunker.chunk_document_sections(
        document_id="doc-test-1",
        document_title="Test Document",
        sections=sections
    )

    assert len(chunks) > 1
    for c in chunks:
        assert len(c.text) <= 250
        assert c.document_id == "doc-test-1"
        assert c.page_number == 1
        assert c.chunk_index >= 0
        assert c.token_count > 0

def test_chunker_overlap_validation():
    with pytest.raises(ValueError, match="chunk_overlap must be strictly less than chunk_size"):
        RecursiveCharacterChunker(chunk_size=100, chunk_overlap=150)

def test_html_parser():
    html = "<html><body><h1>Ledger</h1><p>First paragraph with details.</p></body></html>"
    sections, meta = DocumentParser.parse(html.encode("utf-8"), DocumentFormat.HTML)
    assert len(sections) >= 1
    assert "First paragraph with details" in sections[0]["text"]
