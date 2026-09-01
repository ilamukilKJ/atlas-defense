"""
Conversational Agent for ATLAS.
Orchestrates memory retrieval, response synthesis with Gemini, candidate memory extraction,
and real-time ATLAS trust evaluation.
"""

from typing import List, Dict, Optional
from core.gemini_client import gemini_client, GeminiClient
from memory.memory_models import (
    ChatTurn,
    ChatRequest,
    ChatResponse,
    CandidateMemory,
    MemoryStatus
)
from memory.memory_extractor import memory_extractor, MemoryExtractor
from agent.memory_manager import memory_manager, MemoryManager
from agent.prompts import SYSTEM_AGENT_PROMPT


class AtlasAgent:
    """
    Agent interacting with users and long-term memory protected by ATLAS.
    """

    def __init__(
        self,
        gemini: Optional[GeminiClient] = None,
        mem_manager: Optional[MemoryManager] = None,
        extractor: Optional[MemoryExtractor] = None
    ):
        self.gemini = gemini or gemini_client
        self.memory_manager = mem_manager or memory_manager
        self.extractor = extractor or memory_extractor

    def chat(self, request: ChatRequest) -> ChatResponse:
        """
        Processes a conversational message turn end-to-end:
        1. Memory Retrieval (ACCEPTED only)
        2. Response Generation
        3. Candidate Memory Extraction
        4. ATLAS Trust Evaluation & Routing (ACCEPT / QUARANTINE)
        """
        user_message = request.message
        history_dicts = [{"role": turn.role, "content": turn.content} for turn in (request.history or [])]

        # 1. Retrieve relevant accepted persistent memories
        retrieved_items = self.memory_manager.retrieve_relevant_memories(user_message, top_k=3)
        retrieved_texts = [m.content for m in retrieved_items]

        # 2. Generate response using Gemini
        agent_reply = self.gemini.generate_chat_response(
            user_message=user_message,
            retrieved_memories=retrieved_texts,
            history=history_dicts,
            system_instruction=SYSTEM_AGENT_PROMPT
        )

        # 3. Extract candidate memory from conversational turn
        candidate = self.extractor.extract_from_turn(
            user_message=user_message,
            agent_response=agent_reply
        )

        candidate_mem_out: Optional[CandidateMemory] = None
        mem_status_out: Optional[MemoryStatus] = None
        trust_score_out: Optional[float] = None
        signals_out = None
        decision_reason_out: Optional[str] = None

        # 4. If candidate memory extracted, pass to ATLAS
        if candidate:
            candidate_mem_out = candidate
            saved_item, score, status, reason = self.memory_manager.process_candidate_memory(
                candidate=candidate,
                context_text=user_message,
                enable_atlas=request.enable_atlas
            )
            mem_status_out = status
            trust_score_out = score
            signals_out = saved_item.signals
            decision_reason_out = reason

        return ChatResponse(
            response=agent_reply,
            candidate_memory=candidate_mem_out,
            memory_status=mem_status_out,
            trust_score=trust_score_out,
            signals=signals_out,
            decision_reason=decision_reason_out,
            retrieved_memories=retrieved_texts
        )


# Global agent instance
atlas_agent = AtlasAgent()
