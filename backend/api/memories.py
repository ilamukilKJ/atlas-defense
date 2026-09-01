"""
Memories API Endpoints for ATLAS.
Provides endpoints to list, inspect, analyze, and manage persistent and quarantined memories.
"""

from typing import Optional
import uuid
import datetime
from fastapi import APIRouter, HTTPException, Query
from memory.memory_models import (
    MemoryItem,
    MemoryListResponse,
    MemoryStatus,
    MemorySource,
    CandidateMemory,
    AnalyzeMemoryRequest,
    AnalyzeMemoryResponse
)
from memory.vector_store import global_vector_store
from atlas.trust_engine import trust_engine
from core.embeddings import embedding_service

router = APIRouter(prefix="/memories", tags=["Memories"])


@router.get("", response_model=MemoryListResponse)
async def list_memories(
    status: Optional[MemoryStatus] = Query(None, description="Filter by status (ACCEPTED or QUARANTINED)"),
    search: Optional[str] = Query(None, description="Search query string")
) -> MemoryListResponse:
    """
    Retrieve stored memories with optional status and search filtering.
    """
    items = global_vector_store.list_memories(status=status, query=search)
    total = global_vector_store.count()
    accepted = global_vector_store.count(MemoryStatus.ACCEPTED)
    quarantined = global_vector_store.count(MemoryStatus.QUARANTINED)

    return MemoryListResponse(
        memories=items,
        total=total,
        accepted_count=accepted,
        quarantined_count=quarantined
    )


@router.get("/{memory_id}", response_model=MemoryItem)
async def get_memory_detail(memory_id: str) -> MemoryItem:
    """
    Retrieve full details for a specific memory item.
    """
    item = global_vector_store.get_memory(memory_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Memory '{memory_id}' not found.")
    return item


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str):
    """
    Remove a memory item from storage.
    """
    success = global_vector_store.delete_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Memory '{memory_id}' not found.")
    return {"status": "success", "message": f"Memory '{memory_id}' deleted successfully."}


@router.post("/analyze", response_model=AnalyzeMemoryResponse)
async def analyze_memory_text(request: AnalyzeMemoryRequest) -> AnalyzeMemoryResponse:
    """
    Analyze a custom memory statement using the 6 ATLAS trust signals without necessarily saving it.
    """
    cid = f"cand-{uuid.uuid4().hex[:8]}"
    source_enum = MemorySource.USER_CONVERSATION
    try:
        if request.source:
            source_enum = MemorySource(request.source)
    except Exception:
        pass

    emb = embedding_service.get_embedding(request.content)
    candidate = CandidateMemory(
        id=cid,
        content=request.content,
        category="fact",
        extracted_from_turn=request.context or "",
        source=source_enum,
        embedding=emb
    )

    trust_score, status, signals, contribs, reason = trust_engine.evaluate_candidate(
        candidate=candidate,
        context_text=request.context,
        custom_weights=request.weights
    )

    return AnalyzeMemoryResponse(
        candidate_id=cid,
        content=request.content,
        trust_score=trust_score,
        status=status,
        signals=signals,
        weighted_contributions=contribs,
        decision_reason=reason,
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
