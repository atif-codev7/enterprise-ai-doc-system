# Enterprise AI Document Intelligence System

[![CI/CD Pipeline](https://github.com/portfolio/enterprise-ai-doc-system/actions/workflows/ci.yml/badge.svg)](https://github.com/portfolio/enterprise-ai-doc-system/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-emerald.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%2B%20%7C%20pgvector-blue.svg)](https://github.com/pgvector/pgvector)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14%20App%20Router-black.svg)](https://nextjs.org/)

An enterprise-grade, production-engineered AI Document Intelligence and Retrieval-Augmented Generation (RAG) platform. Part of the **Flagship Architectural Portfolio (Project 3)**, specifically integrated with **Project 1 (PayGuard High-Concurrency Ledger)**.

---

## 🏗️ Architectural Topology

```
+---------------------------------------------------------------------------------------------------+
|                                        NEXT.JS FRONTEND (TS)                                      |
|  - Real-Time Token Streaming (SSE)        - Interactive Inline Citations [Doc X, p. Y]             |
|  - Multi-Format Ingestion Dashboard       - LangGraph Tool Execution Transparency Drawer          |
|  - Prompt-Injection Security Alerts       - Quantitative Ragas Evaluation Benchmark Dashboard    |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  | Server-Sent Events (SSE) & REST
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                       FASTAPI AI SERVICE                                          |
|                                                                                                   |
|  [ Ingestion Engine ]                    [ Multi-Layer Guardrails ]     [ Deterministic Router ]  |
|  - PDF (PyPDF2 page tracking)            - Regex Heuristic Jailbreaks   - Intent Classifier       |
|  - Markdown & HTML Parsing               - Adversarial Threat Scoring   - Canary Leakage Defense  |
|  - Recursive Character Chunker           - Pydantic Schema Validation   - Secret Sanitization     |
|                                                                                                   |
|  [ Vector Retrieval Engine ]             [ LangGraph Workflow Engine ]  [ Quantitative Ragas ]    |
|  - PostgreSQL + pgvector (HNSW)          - TypedDict DocIntelState      - Faithfulness            |
|  - vector_cosine_ops (m=16, ef=64)       - PayGuard Ledger Inquiry      - Context Relevance       |
|  - Dynamic ef_search=40 query runtime    - Financial Velocity Tool      - Answer Relevance        |
+---------------------------------------------------------------------------------------------------+
                                    |                               |
                   +----------------+                               +----------------+
                   v                                                                 v
+---------------------------------------+                         +---------------------------------+
|       POSTGRESQL + PGVECTOR (ACID)    |                         |        PAYGUARD LEDGER DB       |
|  - Extension: vector                  |                         |  - Double-Entry Journal Records |
|  - Table: document_chunks             |                         |  - Row Locks (with_for_update)  |
|  - HNSW Cosine Vector Index           |                         |  - Idempotency Keys (idemp-*)   |
|  - Table: query_audit_logs            |                         |  - Settlement & Audit Trails    |
+---------------------------------------+                         +---------------------------------+
```

---

## 🌟 Key Highlights & Engineering Features

### 1. Multi-Format Ingestion with Recursive Character Chunking
- Ingests **PDF** (extracting text page-by-page), **Markdown** (preserving section hierarchy `#`, `##`, `###`), **HTML**, and **Plaintext**.
- Recursive Character Text Chunker splits text dynamically along natural semantic boundaries (`["\n## ", "\n### ", "\n\n", "\n", ". ", " "]`) with configurable chunk size and overlap.
- Strictly preserves character boundaries, page offsets, section headers, and token estimates.

### 2. PostgreSQL + pgvector HNSW Vector Search
- Leverages PostgreSQL 16 with native `vector` extension.
- Provisions Hierarchical Navigable Small World (**HNSW**) indexes with cosine distance:
  ```sql
  CREATE INDEX idx_chunks_hnsw ON document_chunks 
  USING hnsw (embedding vector_cosine_ops) 
  WITH (m = 16, ef_construction = 64);
  ```
- Dynamically tunes `SET LOCAL hnsw.ef_search = 40;` during user retrieval queries for optimal latency-recall tradeoff.
- Includes embedded fallback vector store for immediate zero-dependency offline local execution and CI testing.

### 3. Token-Streaming RAG Interface with Interactive Inline Citations
- Streams response tokens progressively via Server-Sent Events (SSE) `/api/rag/chat/stream`.
- Embeds interactive inline citation markers directly into streamed tokens: `[Doc 1, p. 2]`.
- Clicking any citation in the Next.js UI reveals the **Citation Inspector Drawer** displaying the exact grounding source snippet, similarity score, document title, and page number.

### 4. Deterministic LangGraph Tool Workflows (PayGuard Ledger Integration)
- Implements a state machine via `langgraph.graph.StateGraph` with typed `DocIntelState`.
- Routes deterministic queries directly into **PayGuard's Financial Ledger Database** (Project 1):
  - `query_payguard_ledger(account_id, limit)`: Inspects double-entry transactions, ACID row-locked balance status, and idempotency keys.
  - `run_financial_analytics(account_id, time_window_days)`: Calculates turnover velocity, variance, and anomaly scores.

### 5. Multi-Layer Prompt-Injection Guardrails & Strict Pydantic Validation
- Multi-layer defense intercepting:
  - System prompt overrides (`ignore all previous instructions`)
  - Jailbreak personas (`DAN mode`, unrestricted personas)
  - Delimiter and XML tag injection (`<system>`, `[developer]`)
  - Privilege escalation & SQL injection probes (`sudo`, `drop table`, `reveal secrets`)
- Strict Pydantic runtime schema validation (`ToolCallValidator`) intercepts malformed or hallucinated tool parameters before execution.
- Automated secret sanitizer redacting API keys and connection URLs from generated text.

### 6. Automated Quantitative Evaluation Suite (Ragas Standards)
- Mathematical scoring engine measuring:
  - **Faithfulness**: Proportion of factual claims in generated answers directly entailed by context passages:
    $$\text{Faithfulness} = \frac{|\text{Claims supported by retrieved context}|}{|\text{Total claims in generated answer}|}$$
  - **Context Relevance**: Signal-to-noise ratio of retrieved chunks relative to the user query.
  - **Answer Relevance**: Semantic intent coverage ratio.
- Production benchmark dataset covering financial ledger semantics, idempotency, and concurrency controls with automated CI/CD SLA quality gating ($\ge 70\%$).

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (optional, for full containerized stack)

### Option A: Run via Docker Compose (Recommended)
```bash
docker-compose up --build
```
- Frontend UI: `http://localhost:3000`
- FastAPI Documentation (Swagger): `http://localhost:8000/docs`
- PostgreSQL pgvector: `localhost:5432`

### Option B: Standalone Local Run (Zero External Dependencies)
1. **Start the FastAPI AI Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start the Next.js Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open `http://localhost:3000` in your browser.

---

## 🧪 Automated Pytest Test Suite

Execute the comprehensive 26-test unit and integration test suite:

```bash
cd backend
python -m pytest -v
```

### Verified Test Matrix:
- `tests/test_chunker.py`: Markdown, HTML, PDF parsing, boundary preservation, overlap validation.
- `tests/test_vector_search.py`: L2 unit vector normalization, memory vector store cosine ranking.
- `tests/test_guardrails.py`: Prompt-injection detection, jailbreaks, Pydantic tool validator, secret redaction.
- `tests/test_payguard_tools.py`: PayGuard ledger inquiry, double-entry verification, financial velocity calculations.
- `tests/test_langgraph_workflow.py`: LangGraph state machine routing, security interception, tool execution.
- `tests/test_ragas_evaluation.py`: Ragas faithfulness scoring, hallucination detection, benchmark dataset validation.
- `tests/test_api_endpoints.py`: `/api/health`, `/api/documents/upload`, `/api/rag/chat`, `/api/rag/chat/stream`, `/api/eval/run`.

**Result:** `26 passed in 6.39s` (100% pass rate).

---

## 📡 API Reference

### 1. Ingest Document
```http
POST /api/documents/upload
Content-Type: multipart/form-data

file: <document.pdf | document.md>
title: "PayGuard Architecture SLA"
doc_format: "markdown"
```

### 2. Stream RAG Chat with Inline Citations (SSE)
```http
POST /api/rag/chat/stream
Content-Type: application/json

{
  "message": "How does PayGuard eliminate race conditions under concurrency?",
  "top_k": 4,
  "use_tools": true
}
```

### 3. Run Automated Ragas Quantitative Benchmark
```http
POST /api/eval/run
Content-Type: application/json

{}
```

Response:
```json
{
  "total_samples": 4,
  "mean_faithfulness": 1.0,
  "mean_context_relevance": 0.725,
  "mean_answer_relevance": 0.686,
  "mean_overall_score": 0.781,
  "passed": true
}
```

---

## ☁️ Production AWS Cloud Deployment (Terraform)

Infrastructure-as-Code is provided under `terraform/`:
- **AWS ECS Fargate**: Serverless container orchestration for the FastAPI AI Service.
- **Amazon Aurora PostgreSQL with pgvector**: RDS parameter group with `shared_preload_libraries = "vector"`.
- **Application Load Balancer (ALB)**: HTTPS listener, health checks `/api/health`.
- **VPC & Security Groups**: Multi-AZ public and private subnets isolating database access.

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

---

## 📄 License
MIT License. Created as part of the Flagship Architectural Portfolio.
