from typing import List, Optional
from fastapi import APIRouter
from app.models.schemas import EvaluationReport, EvaluationSample
from app.evaluation.ragas_evaluator import ragas_evaluator
from app.evaluation.benchmark_dataset import BENCHMARK_SAMPLES

router = APIRouter(prefix="/eval", tags=["Quantitative Evaluation"])

@router.post("/run", response_model=EvaluationReport)
async def run_evaluation(custom_samples: Optional[List[EvaluationSample]] = None):
    """
    Executes automated quantitative evaluation suite measuring Faithfulness,
    Context Relevance, and Answer Relevance based on Ragas standards.
    """
    samples = custom_samples or BENCHMARK_SAMPLES
    report = ragas_evaluator.evaluate_dataset(samples)
    return report

@router.get("/benchmark")
async def get_benchmark_samples():
    """
    Retrieves the standard enterprise benchmark dataset for DocIntel evaluation.
    """
    return {
        "benchmark_name": "PayGuard & DocIntel Architectural Gold Standard",
        "sample_count": len(BENCHMARK_SAMPLES),
        "samples": [s.model_dump() for s in BENCHMARK_SAMPLES]
    }
