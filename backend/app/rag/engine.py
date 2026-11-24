import time
from typing import Dict, Any
from app.workflows.graph import docintel_graph
from app.workflows.state import DocIntelState
from app.models.schemas import ChatQueryRequest, ChatQueryResponse, GuardrailCheckResult

class RAGEngine:
    """
    RAG Engine wrapping LangGraph state machine execution,
    returning structured ChatQueryResponse models.
    """

    @classmethod
    def execute_query(cls, request: ChatQueryRequest) -> ChatQueryResponse:
        t_start = time.perf_counter()

        initial_state: DocIntelState = {
            "query": request.message,
            "conversation_id": request.conversation_id,
            "top_k": request.top_k,
            "use_tools": request.use_tools,
            "temperature": request.temperature,
            "guardrail": None,
            "intent": "document_search",
            "target_account_id": None,
            "retrieved_chunks": [],
            "tool_executions": [],
            "citations": [],
            "final_answer": "",
            "status": "initialized",
            "errors": []
        }

        final_state = docintel_graph.invoke(initial_state)
        latency = round((time.perf_counter() - t_start) * 1000.0, 2)

        guardrail = final_state.get("guardrail") or GuardrailCheckResult(
            is_safe=True, risk_score=0.0, violated_rules=[]
        )

        return ChatQueryResponse(
            answer=final_state.get("final_answer", ""),
            citations=final_state.get("citations", []),
            tool_executions=final_state.get("tool_executions", []),
            guardrail=guardrail,
            latency_ms=latency,
            retrieved_chunks_count=len(final_state.get("retrieved_chunks", []))
        )

rag_engine = RAGEngine()
