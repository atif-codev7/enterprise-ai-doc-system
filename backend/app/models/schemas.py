from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class DocumentFormat(str, Enum):
    PDF = "pdf"
    MARKDOWN = "markdown"
    TXT = "txt"
    HTML = "html"

class DocumentMetadata(BaseModel):
    title: str = Field(..., description="Title of the document")
    author: Optional[str] = Field(None, description="Author or source entity")
    format: DocumentFormat = Field(DocumentFormat.TXT, description="File format")
    total_pages: int = Field(1, ge=1, description="Total number of pages")
    file_size_bytes: int = Field(0, ge=0, description="Size in bytes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    custom_attributes: Dict[str, Any] = Field(default_factory=dict)

class DocumentChunk(BaseModel):
    id: str = Field(..., description="Unique chunk UUID")
    document_id: str = Field(..., description="Parent document UUID")
    document_title: str = Field(..., description="Parent document title")
    chunk_index: int = Field(..., ge=0, description="0-indexed position within document")
    text: str = Field(..., min_length=1, description="Raw chunk text")
    page_number: int = Field(1, ge=1, description="Page number where chunk originates")
    start_char: int = Field(0, ge=0, description="Character offset start")
    end_char: int = Field(0, ge=0, description="Character offset end")
    section_header: Optional[str] = Field(None, description="Nearby markdown/document section header")
    token_count: int = Field(0, ge=0)
    embedding: Optional[List[float]] = Field(None, description="Vector embedding representation")

class DocumentUploadResponse(BaseModel):
    document_id: str
    title: str
    format: DocumentFormat
    chunk_count: int
    total_tokens: int
    created_at: datetime
    message: str = "Document successfully ingested and indexed with HNSW vectors."

class ChunkSearchResult(BaseModel):
    chunk: DocumentChunk
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
    rank: int = Field(..., ge=1, description="Result rank")

class InlineCitation(BaseModel):
    citation_id: int = Field(..., description="Citation numeric index [1], [2], etc.")
    document_id: str
    document_title: str
    chunk_id: str
    page_number: int
    snippet: str
    relevance_score: float

class GuardrailCheckResult(BaseModel):
    is_safe: bool = Field(..., description="True if no prompt injection or malicious pattern detected")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Calculated threat probability score")
    violated_rules: List[str] = Field(default_factory=list)
    sanitization_applied: bool = False
    flagged_snippet: Optional[str] = None

class ChatQueryRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="User prompt or inquiry")
    conversation_id: Optional[str] = Field(None, description="Optional conversational session ID")
    top_k: int = Field(4, ge=1, le=20, description="Number of vector chunks to retrieve")
    use_tools: bool = Field(True, description="Enable deterministic LangGraph tool calling")
    temperature: float = Field(0.1, ge=0.0, le=1.0, description="LLM temperature")

class ToolExecutionTrace(BaseModel):
    tool_name: str
    input_parameters: Dict[str, Any]
    output_result: Dict[str, Any]
    execution_time_ms: float
    status: str = "success"

class ChatQueryResponse(BaseModel):
    answer: str
    citations: List[InlineCitation] = Field(default_factory=list)
    tool_executions: List[ToolExecutionTrace] = Field(default_factory=list)
    guardrail: GuardrailCheckResult
    latency_ms: float
    retrieved_chunks_count: int

# PayGuard Tool Schemas
class PayGuardLedgerQuery(BaseModel):
    account_id: str = Field(..., description="Target PayGuard account UUID or code (e.g. ACC-1001)")
    limit: int = Field(5, ge=1, le=50, description="Max entries to retrieve")
    
    @field_validator("account_id")
    def validate_account(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("account_id cannot be blank")
        return v.strip().upper()

class FinancialAnalyticsQuery(BaseModel):
    account_id: str = Field(..., description="Target account identifier")
    time_window_days: int = Field(30, ge=1, le=365, description="Time window in days")
    metrics: List[str] = Field(default=["variance", "velocity", "anomaly_score"])

# Evaluation Schemas (Ragas)
class EvaluationSample(BaseModel):
    question: str
    contexts: List[str]
    answer: str
    ground_truth: Optional[str] = None

class RagasMetricResult(BaseModel):
    faithfulness: float = Field(..., ge=0.0, le=1.0)
    context_relevance: float = Field(..., ge=0.0, le=1.0)
    answer_relevance: float = Field(..., ge=0.0, le=1.0)
    overall_ragas_score: float = Field(..., ge=0.0, le=1.0)
    verdict: str = "PASSED"
    breakdown: Dict[str, Any] = Field(default_factory=dict)

class EvaluationReport(BaseModel):
    total_samples: int
    mean_faithfulness: float
    mean_context_relevance: float
    mean_answer_relevance: float
    mean_overall_score: float
    passed: bool
    benchmark_timestamp: datetime = Field(default_factory=datetime.utcnow)
    sample_evaluations: List[Dict[str, Any]]
