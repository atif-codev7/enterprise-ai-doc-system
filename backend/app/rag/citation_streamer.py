import asyncio
import json
import time
from typing import AsyncGenerator, Dict, Any
from app.workflows.graph import docintel_graph
from app.workflows.state import DocIntelState

async def stream_rag_tokens(
    query: str,
    top_k: int = 4,
    use_tools: bool = True,
    temperature: float = 0.1
) -> AsyncGenerator[str, None]:
    """
    Asynchronous Server-Sent Events (SSE) generator streaming tokens,
    guardrail security alerts, tool execution states, and inline citations.
    """
    t_start = time.perf_counter()

    initial_state: DocIntelState = {
        "query": query,
        "conversation_id": None,
        "top_k": top_k,
        "use_tools": use_tools,
        "temperature": temperature,
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

    # Execute deterministic LangGraph pipeline
    final_state = await asyncio.to_thread(docintel_graph.invoke, initial_state)

    # 1. Stream Guardrail status event
    if final_state.get("guardrail"):
        yield f"data: {json.dumps({'type': 'guardrail', 'data': final_state['guardrail'].model_dump()})}\n\n"
        await asyncio.sleep(0.01)

    # If intercepted by guardrails, stream rejection tokens and complete
    if final_state.get("status") == "guardrail_rejected":
        yield f"data: {json.dumps({'type': 'guardrail_alert', 'data': {'risk_score': final_state['guardrail'].risk_score, 'violations': final_state['guardrail'].violated_rules}})}\n\n"
        for word in final_state["final_answer"].split(" "):
            yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"
            await asyncio.sleep(0.01)
        total_time_ms = round((time.perf_counter() - t_start) * 1000.0, 2)
        yield f"data: {json.dumps({'type': 'done', 'latency_ms': total_time_ms})}\n\n"
        return

    # 2. Stream Tool Execution Events
    for tool_trace in final_state.get("tool_executions", []):
        yield f"data: {json.dumps({'type': 'tool_start', 'tool_name': tool_trace.tool_name, 'input': tool_trace.input_parameters})}\n\n"
        await asyncio.sleep(0.02)
        yield f"data: {json.dumps({'type': 'tool_end', 'tool_name': tool_trace.tool_name, 'result': tool_trace.output_result, 'execution_ms': tool_trace.execution_time_ms})}\n\n"
        await asyncio.sleep(0.02)

    # 3. Stream Inline Citations metadata
    for citation in final_state.get("citations", []):
        yield f"data: {json.dumps({'type': 'citation', 'data': citation.model_dump()})}\n\n"
        await asyncio.sleep(0.01)

    # 4. Stream Tokens progressively
    answer_text = final_state.get("final_answer", "")
    # Split text into natural token-like chunks (words or word clusters)
    words = answer_text.split(" ")
    for word in words:
        yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"
        await asyncio.sleep(0.015) # Smooth realistic streaming cadence

    # 5. Stream Completion Event
    total_time_ms = round((time.perf_counter() - t_start) * 1000.0, 2)
    yield f"data: {json.dumps({'type': 'done', 'latency_ms': total_time_ms})}\n\n"
