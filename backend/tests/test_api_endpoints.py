import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "vector_store_chunks" in data
    assert "guardrail_engine" in data

def test_document_upload_and_listing():
    # Ingest a test specification via raw_text
    response = client.post(
        "/api/documents/upload",
        data={
            "title": "Webhook Reliability Contract",
            "doc_format": "markdown",
            "raw_text": "## Retry Strategy\nThe Reliable Webhook Engine utilizes ARQ workers with exponential backoff 1s 2s 4s 8s 16s."
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Webhook Reliability Contract"
    assert data["chunk_count"] >= 1
    doc_id = data["document_id"]

    # List documents
    list_res = client.get("/api/documents")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert any(d["document_id"] == doc_id for d in list_data["documents"])

    # Clean up test doc
    del_res = client.delete(f"/api/documents/{doc_id}")
    assert del_res.status_code == 200

def test_rag_chat_endpoint():
    response = client.post(
        "/api/rag/chat",
        json={"message": "Query PayGuard ledger for ACC-1001", "top_k": 3, "use_tools": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "ACC-1001" in data["answer"]
    assert len(data["tool_executions"]) >= 1

def test_rag_streaming_endpoint():
    response = client.post(
        "/api/rag/chat/stream",
        json={"message": "What is the double-entry bookkeeping schema in PayGuard?", "top_k": 2}
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    content = response.text
    assert "data: " in content
    assert '"type": "token"' in content
    assert '"type": "done"' in content

def test_eval_run_endpoint():
    response = client.post("/api/eval/run")
    assert response.status_code == 200
    data = response.json()
    assert data["total_samples"] > 0
    assert data["mean_faithfulness"] >= 0.70
    assert data["passed"] is True
