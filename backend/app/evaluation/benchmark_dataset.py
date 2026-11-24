from typing import List
from app.models.schemas import EvaluationSample

BENCHMARK_SAMPLES: List[EvaluationSample] = [
    EvaluationSample(
        question="How does PayGuard eliminate race conditions and prevent double-spending under high concurrency?",
        contexts=[
            "PayGuard enforces ACID transactions utilizing PostgreSQL row-level locking via SELECT with_for_update().",
            "This row-level lock serializes concurrent balance mutations on debtor and creditor accounts, entirely eliminating race conditions and preventing double-spending across parallel worker threads.",
            "Additionally, client-generated idempotency keys are tracked in Redis and PostgreSQL to ensure duplicate transfer requests return cached 200 responses without re-debiting balances."
        ],
        answer="PayGuard eliminates race conditions and prevents double-spending by utilizing PostgreSQL row-level locking with with_for_update() to serialize concurrent account mutations under strict ACID isolation, combined with client-generated idempotency keys that guarantee idempotent transfer execution.",
        ground_truth="PostgreSQL row-level locking with with_for_update() and idempotency keys."
    ),
    EvaluationSample(
        question="What is the architecture of the double-entry bookkeeping schema in PayGuard?",
        contexts=[
            "In PayGuard, every financial transaction produces a balanced double-entry journal entry.",
            "Every debit to an account is strictly matched with an offsetting credit of equal amount to a counterparty or settlement account.",
            "The system maintains mathematical balance where total debits equal total credits, audited continuously with zero tolerance for floating imbalances."
        ],
        answer="PayGuard enforces a double-entry bookkeeping schema where every transaction creates paired journal entries such that every debit is matched with an offsetting credit of identical magnitude, guaranteeing total debits equal total credits across the ledger.",
        ground_truth="Every debit is balanced by an offsetting credit of equal amount."
    ),
    EvaluationSample(
        question="What vector indexing algorithm and distance metric does the Enterprise AI Doc System use in PostgreSQL?",
        contexts=[
            "The document intelligence system provisions an HNSW (Hierarchical Navigable Small World) index in PostgreSQL pgvector.",
            "It configures vector_cosine_ops distance with an index construction parameter of m=16 and ef_construction=64, dynamically adjusting ef_search=40 during retrieval queries."
        ],
        answer="The system configures an HNSW index via PostgreSQL pgvector with vector_cosine_ops distance metric, setting m=16, ef_construction=64, and runtime query parameter ef_search=40.",
        ground_truth="HNSW index with vector_cosine_ops, m=16, ef_construction=64."
    ),
    EvaluationSample(
        question="How does the system defend against prompt injection and unauthorized tool parameters?",
        contexts=[
            "Security is enforced at two distinct layers: a heuristic prompt-injection guardrail that intercepts system override attempts and jailbreak tokens, and strict Pydantic runtime schema validation on all LangGraph tool calls.",
            "If an input attempts privilege escalation or malicious delimiters, the guardrail triggers an intervention alert and prevents downstream LLM execution."
        ],
        answer="The system defends against attacks through a multi-layer prompt-injection guardrail scanning for jailbreak tokens and instruction overrides, paired with strict Pydantic schema validation that blocks unauthorized or hallucinated tool parameters.",
        ground_truth="Prompt-injection guardrail combined with strict Pydantic tool-call validation."
    )
]
