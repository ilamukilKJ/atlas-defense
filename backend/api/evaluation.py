"""
Evaluation API Endpoints for ATLAS.
Provides empirical metrics on Attack Success Rate, Detection Rate, Precision,
Recall, F1-Score, and False Positive Rate.
"""

from fastapi import APIRouter
from evaluation.metrics import EvaluationSummary
from evaluation.experiment_runner import experiment_runner

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.get("/summary", response_model=EvaluationSummary)
async def get_evaluation_summary() -> EvaluationSummary:
    """
    Retrieve current empirical evaluation summary metrics.
    """
    return experiment_runner.get_summary()


@router.post("/run", response_model=EvaluationSummary)
async def run_fresh_evaluation() -> EvaluationSummary:
    """
    Trigger a fresh benchmark evaluation across all synthetic attack and benign test items.
    """
    return experiment_runner.run_benchmark()
