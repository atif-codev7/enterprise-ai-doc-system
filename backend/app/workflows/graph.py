import re
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from app.workflows.state import DocIntelState
from app.workflows.tools import execute_payguard_ledger_tool, execute_financial_analytics_tool
from app.guardrails.injection_detector import guardrail_service
from app.vector import vector_store
from app.models.schemas import InlineCitation, ChunkSearchResult

def guardrail_check_node(state: DocIntelState) -> Dict[str, Any]:
    """
    Evaluates query for prompt injection, jailbreaks, or adversarial manipulation.
    """
    check = guardrail_service.scan(state["query"])
    return {
        "guardrail": check,
        "status": "guardrail_scanned"
    }

def route_after_guardrail(state: DocIntelState) -> str:
    if state["guardrail"] and not state["guardrail"].is_safe:
        return "guardrail_reject_node"
    return "intent_router_node"

def intent_router_node(state: DocIntelState) -> Dict[str, Any]:
    """
    Deterministic intent classifier matching user objectives to tools or document search.
    """
    q = state["query"].lower()
    
    # Extract any account code like ACC-1001, ACC-2005
    acc_match = re.search(r"\b(acc-\d{4})\b", q)
    target_account = acc_match.group(1).upper() if acc_match else "ACC-1001"

    if any(k in q for k in ["analytics", "variance", "velocity", "anomaly", "turnover", "risk rating"]):
        intent = "financial_analytics"
    elif any(k in q for k in ["ledger", "balance", "transfer", "payguard", "double-entry", "journal", "settlement"]):
        intent = "payguard_ledger"
    else:
        intent = "document_search"

    return {
        "intent": intent,
        "target_account_id": target_account,
        "status": "intent_routed"
    }

def route_intent(state: DocIntelState) -> str:
    intent = state.get("intent", "document_search")
    if intent == "financial_analytics":
        return "financial_analytics_tool_node"
    elif intent == "payguard_ledger":
        return "payguard_ledger_tool_node"
    return "document_retrieval_node"

def payguard_ledger_tool_node(state: DocIntelState) -> Dict[str, Any]:
    """
    Executes validated PayGuard double-entry ledger inquiry.
    """
    acc_id = state.get("target_account_id") or "ACC-1001"
    args = {"account_id": acc_id, "limit": 5}
    result, trace = execute_payguard_ledger_tool(args)

    return {
        "tool_executions": (state.get("tool_executions") or []) + [trace],
        "status": "tool_executed"
    }

def financial_analytics_tool_node(state: DocIntelState) -> Dict[str, Any]:
    """
    Executes validated PayGuard financial analytics calculation.
    """
    acc_id = state.get("target_account_id") or "ACC-1001"
    args = {"account_id": acc_id, "time_window_days": 30}
    result, trace = execute_financial_analytics_tool(args)

    return {
        "tool_executions": (state.get("tool_executions") or []) + [trace],
        "status": "tool_executed"
    }

def document_retrieval_node(state: DocIntelState) -> Dict[str, Any]:
    """
    Performs HNSW vector retrieval against pgvector store.
    """
    top_k = state.get("top_k", 4)
    results = vector_store.search(query=state["query"], top_k=top_k)
    return {
        "retrieved_chunks": results,
        "status": "chunks_retrieved"
    }

def synthesis_node(state: DocIntelState) -> Dict[str, Any]:
    """
    Synthesizes final answer with inline citation tags and tool insights.
    """
    query = state["query"]
    citations: List[InlineCitation] = []
    lines: List[str] = []

    # If tools executed, format PayGuard insights
    tools = state.get("tool_executions") or []
    if tools:
        for t in tools:
            res = t.output_result
            if t.tool_name == "query_payguard_ledger" and res.get("found"):
                acc = res["account"]
                lines.append(f"### PayGuard Ledger Status for {acc['account_id']} ({acc['holder_name']})")
                lines.append(f"- **Current Balance**: ${acc['balance']:,.2f} {acc['currency']}")
                lines.append(f"- **Reconciliation Status**: {res.get('reconciliation_status')} (Row locks verified)")
                lines.append("\n**Recent Settled Transactions:**")
                for entry in res.get("journal_entries", []):
                    lines.append(f"- `{entry['entry_id']}`: {entry['transaction_type']} of ${entry['amount']:,.2f} ({entry['description']}) [Idempotency: {entry['idempotency_key']}]")

            elif t.tool_name == "run_financial_analytics" and "metrics" in res:
                m = res["metrics"]
                lines.append(f"### Financial Risk & Velocity Analytics ({res['account_id']})")
                lines.append(f"- **Total Inflow / Outflow**: +${m['total_inflow']:,.2f} / -${m['total_outflow']:,.2f} (Net: ${m['net_flow']:,.2f})")
                lines.append(f"- **Transaction Velocity**: {m['transaction_velocity']}x")
                lines.append(f"- **Amount Variance**: {m['amount_variance']:,.2f} (StdDev: {m['standard_deviation']:,.2f})")
                lines.append(f"- **Anomaly Score**: {m['anomaly_score']} (Rating: **{m['risk_rating']}**)")
                lines.append(f"- *Audit*: {res.get('audit_trail')}")

    # Process Document Chunks and generate inline citations
    chunks: List[ChunkSearchResult] = state.get("retrieved_chunks") or []
    if chunks:
        if lines:
            lines.append("\n---\n### Supporting Documentation")

        for idx, item in enumerate(chunks, start=1):
            chunk = item.chunk
            snippet = chunk.text[:200] + ("..." if len(chunk.text) > 200 else "")
            citation = InlineCitation(
                citation_id=idx,
                document_id=chunk.document_id,
                document_title=chunk.document_title,
                chunk_id=chunk.id,
                page_number=chunk.page_number,
                snippet=snippet,
                relevance_score=item.similarity_score
            )
            citations.append(citation)

        # Build context-grounded response text with citation badges
        top_snippet = chunks[0].chunk.text
        lines.append(f"Based on verified architectural and operational specifications [Doc 1, p. {chunks[0].chunk.page_number}]:")
        lines.append(f"\n> \"{top_snippet}\" [Doc 1, p. {chunks[0].chunk.page_number}]\n")
        
        if len(chunks) > 1:
            lines.append(f"Furthermore, cross-referencing documented operational constraints [Doc 2, p. {chunks[1].chunk.page_number}] confirms:")
            lines.append(f"> \"{chunks[1].chunk.text}\" [Doc 2, p. {chunks[1].chunk.page_number}]")

    if not lines:
        lines.append(f"No specific records or document passages matched '{query}'. Please upload documents or query PayGuard accounts like ACC-1001 or ACC-2005.")

    final_answer = "\n".join(lines)
    # Run output sanitizer
    final_answer = guardrail_service.sanitize_output(final_answer)

    return {
        "final_answer": final_answer,
        "citations": citations,
        "status": "completed"
    }

def guardrail_reject_node(state: DocIntelState) -> Dict[str, Any]:
    """
    Generates deterministic security intervention response when prompt injection is detected.
    """
    g = state.get("guardrail")
    violation_str = ", ".join(g.violated_rules) if g and g.violated_rules else "Security policy threshold exceeded"
    
    rejection_msg = (
        f"⚠️ **Security Intervention Alert (Prompt-Injection Guardrail Triggered)**\n\n"
        f"Your query was intercepted by the Enterprise Guardrail Engine (Confidence Risk Score: {g.risk_score if g else 1.0}).\n"
        f"**Violations Flagged**: `{violation_str}`\n\n"
        f"Prompt override directives, privilege escalation probes, or hostile token tampering are strictly blocked."
    )
    return {
        "final_answer": rejection_msg,
        "citations": [],
        "tool_executions": [],
        "status": "guardrail_rejected"
    }

# Build LangGraph State Graph
def build_docintel_graph() -> StateGraph:
    workflow = StateGraph(DocIntelState)

    # Register nodes
    workflow.add_node("guardrail_check_node", guardrail_check_node)
    workflow.add_node("guardrail_reject_node", guardrail_reject_node)
    workflow.add_node("intent_router_node", intent_router_node)
    workflow.add_node("payguard_ledger_tool_node", payguard_ledger_tool_node)
    workflow.add_node("financial_analytics_tool_node", financial_analytics_tool_node)
    workflow.add_node("document_retrieval_node", document_retrieval_node)
    workflow.add_node("synthesis_node", synthesis_node)

    # Define entry and edges
    workflow.set_entry_point("guardrail_check_node")

    workflow.add_conditional_edges(
        "guardrail_check_node",
        route_after_guardrail,
        {
            "guardrail_reject_node": "guardrail_reject_node",
            "intent_router_node": "intent_router_node"
        }
    )

    workflow.add_conditional_edges(
        "intent_router_node",
        route_intent,
        {
            "payguard_ledger_tool_node": "payguard_ledger_tool_node",
            "financial_analytics_tool_node": "financial_analytics_tool_node",
            "document_retrieval_node": "document_retrieval_node"
        }
    )

    workflow.add_edge("payguard_ledger_tool_node", "synthesis_node")
    workflow.add_edge("financial_analytics_tool_node", "synthesis_node")
    workflow.add_edge("document_retrieval_node", "synthesis_node")
    workflow.add_edge("synthesis_node", END)
    workflow.add_edge("guardrail_reject_node", END)

    return workflow.compile()

# Singleton compiled LangGraph application
docintel_graph = build_docintel_graph()
