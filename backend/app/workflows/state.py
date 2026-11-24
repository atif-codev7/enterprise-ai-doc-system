from typing import TypedDict, List, Dict, Any, Optional
from app.models.schemas import (
    GuardrailCheckResult, ChunkSearchResult, ToolExecutionTrace, InlineCitation
)

class DocIntelState(TypedDict):
    """
    Deterministic typed state maintained across LangGraph workflow nodes.
    """
    query: str
    conversation_id: Optional[str]
    top_k: int
    use_tools: bool
    temperature: float
    guardrail: Optional[GuardrailCheckResult]
    intent: str
    target_account_id: Optional[str]
    retrieved_chunks: List[ChunkSearchResult]
    tool_executions: List[ToolExecutionTrace]
    citations: List[InlineCitation]
    final_answer: str
    status: str
    errors: List[str]
