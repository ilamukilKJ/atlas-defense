"""
Agent package for ATLAS.
"""

from agent.prompts import SYSTEM_AGENT_PROMPT, MEMORY_EXTRACTION_PROMPT
from agent.memory_manager import MemoryManager, memory_manager
from agent.agent import AtlasAgent, atlas_agent

__all__ = [
    "SYSTEM_AGENT_PROMPT",
    "MEMORY_EXTRACTION_PROMPT",
    "MemoryManager",
    "memory_manager",
    "AtlasAgent",
    "atlas_agent"
]
