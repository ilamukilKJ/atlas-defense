"""
Memory Data Models for ATLAS.
Defines Pydantic representations for candidate memories, persistent memories,
trust signal breakdowns, and API request/response structures.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import datetime


class MemoryStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    QUARANTINED = "QUARANTINED"
    PENDING_ANALYSIS = "PENDING_ANALYSIS"


class MemorySource(str, Enum):
    USER_CONVERSATION = "USER_CONVERSATION"
    AGENT_INFERENCE = "AGENT_INFERENCE"
    SYSTEM_PROMPT = "SYSTEM_PROMPT"
    ATTACK_SIMULATOR = "ATTACK_SIMULATOR"


class TrustSignalsBreakdown(BaseModel):
    semantic_relevance: float = Field(..., ge=0.0, le=1.0, description="Alignment with active conversational task context")
    embedding_anomaly: float = Field(..., ge=0.0, le=1.0, description="Outlier score from Isolation Forest in latent embedding space")
    historical_consistency: float = Field(..., ge=0.0, le=1.0, description="Absence of contradiction with prior accepted memories")
    behavioral_consistency: float = Field(..., ge=0.0, le=1.0, description="Alignment with established user behavior, preferences, and interaction history")
    source_reliability: float = Field(..., ge=0.0, le=1.0, description="Trustworthiness and authority level of the input originator")
    temporal_trust: float = Field(..., ge=0.0, le=1.0, description="Temporal decay stability and burst injection defense factor")


class CandidateMemory(BaseModel):
    id: str
    content: str
    category: str = "fact"
    extracted_from_turn: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    source: MemorySource = MemorySource.USER_CONVERSATION
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence score")
    should_persist: bool = Field(default=True, description="Whether candidate meets long-term persistence criteria")
    embedding: Optional[List[float]] = None


class MemoryItem(BaseModel):
    id: str
    content: str
    category: str = "fact"
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    source: str = "USER_CONVERSATION"
    status: MemoryStatus = MemoryStatus.ACCEPTED
    trust_score: float = Field(..., ge=0.0, le=1.0)
    anomaly_score: float = Field(default=0.0, ge=0.0, le=1.0)
    signals: TrustSignalsBreakdown
    decision_reason: str = ""
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# API Models
class ChatTurn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatTurn]] = []
    enable_atlas: bool = True


class ChatResponse(BaseModel):
    response: str
    candidate_memory: Optional[CandidateMemory] = None
    memory_status: Optional[MemoryStatus] = None
    trust_score: Optional[float] = None
    signals: Optional[TrustSignalsBreakdown] = None
    decision_reason: Optional[str] = None
    retrieved_memories: List[str] = []


class AnalyzeMemoryRequest(BaseModel):
    content: str
    context: Optional[str] = ""
    source: Optional[str] = "USER_CONVERSATION"
    weights: Optional[Dict[str, float]] = None


class AnalyzeMemoryResponse(BaseModel):
    candidate_id: str
    content: str
    trust_score: float
    status: MemoryStatus
    signals: TrustSignalsBreakdown
    weighted_contributions: Dict[str, float]
    decision_reason: str
    timestamp: str


class MemoryListResponse(BaseModel):
    memories: List[MemoryItem]
    total: int
    accepted_count: int
    quarantined_count: int
