"""
Evaluation package for ATLAS.
"""

from evaluation.metrics import ConfusionMatrix, EvaluationSummary, compute_metrics
from evaluation.experiment_runner import (
    ExperimentRunner,
    experiment_runner,
    BENCHMARK_DATASET
)

__all__ = [
    "ConfusionMatrix",
    "EvaluationSummary",
    "compute_metrics",
    "ExperimentRunner",
    "experiment_runner",
    "BENCHMARK_DATASET"
]
