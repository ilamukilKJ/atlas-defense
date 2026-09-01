"""
Chat API Endpoints for ATLAS.
Provides the conversational endpoint with real-time memory retrieval, candidate extraction,
and ATLAS trust protection.
"""

from fastapi import APIRouter, HTTPException
from memory.memory_models import ChatRequest, ChatResponse
from agent.agent import atlas_agent

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Handle user message turn, retrieve safe persistent memory, generate reply,
    and evaluate any candidate memory through ATLAS.
    """
    try:
        return atlas_agent.chat(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")
