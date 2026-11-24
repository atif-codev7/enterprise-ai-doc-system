import pytest
from app.evaluation.ragas_evaluator import ragas_evaluator
from app.evaluation.benchmark_dataset import BENCHMARK_SAMPLES
from app.models.schemas import EvaluationSample

def test_ragas_high_faithfulness():
    sample = EvaluationSample(
        question="How does PayGuard handle concurrent transfers?",
        contexts=[
            "PayGuard applies PostgreSQL row locks using SELECT with_for_update().",
            "This serializes concurrent transactions and completely stops double spending."
        ],
        answer="PayGuard applies row locks using SELECT with_for_update() which serializes concurrent transactions and stops double spending.",
        ground_truth="PostgreSQL row-level locking with with_for_update()."
    )

    result = ragas_evaluator.evaluate_sample(sample)
    assert result.faithfulness >= 0.80
    assert result.verdict == "PASSED"

def test_ragas_low_faithfulness_hallucination():
    sample = EvaluationSample(
        question="What database does PayGuard use?",
        contexts=[
            "PayGuard uses PostgreSQL and Redis for financial ledger storage."
        ],
        answer="PayGuard is built on MongoDB Atlas clusters using decentralized Cassandra blockchain consensus nodes.",
        ground_truth="PostgreSQL"
    )

    result = ragas_evaluator.evaluate_sample(sample)
    # The hallucinated answer claims have almost zero overlap with the context
    assert result.faithfulness < 0.50
    assert result.verdict == "FAILED"

def test_ragas_benchmark_dataset():
    report = ragas_evaluator.evaluate_dataset(BENCHMARK_SAMPLES)
    assert report.total_samples == len(BENCHMARK_SAMPLES)
    assert report.mean_faithfulness >= 0.75
    assert report.mean_context_relevance >= 0.50
    assert report.mean_overall_score >= 0.65
    assert report.passed is True
