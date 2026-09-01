"""
ATLAS Trust Analysis API Endpoints.
Provides diagnostic tools to analyze arbitrary candidate memories, inspect signal weights,
and adjust security thresholds.
"""

from fastapi import APIRouter
from memory.memory_models import AnalyzeMemoryRequest, AnalyzeMemoryResponse
from api.memories import analyze_memory_text
from core.settings import settings

router = APIRouter(prefix="/atlas", tags=["ATLAS Trust Engine"])


@router.post("/analyze", response_model=AnalyzeMemoryResponse)
async def atlas_analyze_endpoint(request: AnalyzeMemoryRequest) -> AnalyzeMemoryResponse:
    """
    Detailed ATLAS Trust Analysis for an individual candidate memory across the six signals.
    """
    return await analyze_memory_text(request)


@router.get("/config")
async def get_atlas_configuration():
    """
    Get current default signal weights and trust threshold.
    """
    return {
        "threshold": settings.ATLAS_TRUST_THRESHOLD,
        "weights": settings.SIGNAL_WEIGHTS,
        "signals": [
            {"id": "semantic_relevance", "name": "Semantic Relevance", "description": "Measures semantic alignment with active conversational context.", "default_weight": 0.20},
            {"id": "embedding_anomaly", "name": "Embedding Anomaly Detection", "description": "Isolation Forest latent outlier detection on unit sphere embeddings.", "default_weight": 0.20},
            {"id": "historical_consistency", "name": "Historical Consistency", "description": "Detects conflicts or unauthorized overwrites against persistent memories.", "default_weight": 0.20},
            {"id": "behavioral_consistency", "name": "Behavioral Consistency", "description": "Detects covert prompt injection, backdoor directives, and role hijack patterns.", "default_weight": 0.15},
            {"id": "source_reliability", "name": "Source Reliability", "description": "Evaluates origin authority and channel trust level.", "default_weight": 0.15},
            {"id": "temporal_trust", "name": "Temporal Trust", "description": "Guards against burst attacks and rapid memory churn.", "default_weight": 0.10}
        ]
    }
