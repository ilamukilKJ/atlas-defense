"""
ATLAS Six Trust Signals.
Implements the mathematical and heuristic evaluation logic for each orthogonal
security signal in the ATLAS trust engine.

The six signals are:
1. semantic_relevance: Contextual alignment with active conversational turn.
2. embedding_anomaly: Isolation Forest outlier detection in latent embedding space.
3. historical_consistency: Contradiction and direct overwrite detection against persistent memories.
4. behavioral_consistency: Alignment with established user behavioral preferences and interaction history.
5. source_reliability: Configurable authority mapping for input origin channels.
6. temporal_trust: Transaction pacing, reinforcement stability, and burst defense factor.
"""

import re
from typing import List, Optional, Dict
import numpy as np
from core.settings import settings
from core.embeddings import embedding_service
from atlas.anomaly_detector import anomaly_detector
from memory.vector_store import global_vector_store
from memory.memory_models import MemoryStatus, MemorySource


class TrustSignals:
    """
    Evaluator for the six ATLAS trust signals.
    Each signal produces a normalized score strictly bounded between 0.0 and 1.0.
    """

    @staticmethod
    def evaluate_semantic_relevance(candidate_text: str, context_text: Optional[str] = None) -> float:
        """
        Signal 1: Semantic Relevance (0.0 to 1.0)
        Evaluates how closely the candidate memory aligns with the active conversational context.
        """
        if not context_text or not context_text.strip():
            return 0.75

        emb_candidate = embedding_service.get_embedding(candidate_text)
        emb_context = embedding_service.get_embedding(context_text)

        similarity = embedding_service.cosine_similarity(emb_candidate, emb_context)
        # Direct bounded cosine similarity
        score = 0.10 + 0.90 * similarity
        return float(np.clip(score, 0.05, 1.0))

    @staticmethod
    def evaluate_embedding_anomaly(candidate_embedding: List[float]) -> float:
        """
        Signal 2: Embedding Anomaly (0.0 to 1.0)
        Uses Isolation Forest in latent embedding space.
        Higher score = normal/in-distribution (safe), Lower score = statistical outlier/anomaly.
        """
        if not candidate_embedding:
            return 0.5
        return anomaly_detector.compute_anomaly_score(candidate_embedding)

    @staticmethod
    def evaluate_historical_consistency(candidate_text: str, candidate_embedding: List[float]) -> float:
        """
        Signal 3: Historical Consistency (0.0 to 1.0)
        Detects factual contradictions or unauthorized overwrites against existing accepted memories.
        
        TODO (Research Implementation / Extension): Replace baseline contradiction heuristics
        with a formal Natural Language Inference (NLI) cross-encoder model for entailment vs contradiction.
        """
        accepted_memories = global_vector_store.list_memories(status=MemoryStatus.ACCEPTED)
        if not accepted_memories:
            return 0.90  # No prior constraints, default high consistency

        # Domain predicate clusters where asserting distinct items represents a factual conflict
        domain_clusters = [
            {"python", "java", "rust", "golang", "c++", "typescript", "javascript", "ruby", "c#", "php"},
            {"postgres", "postgresql", "mysql", "mongodb", "redis", "oracle", "sqlite", "dynamodb"},
            {"aws", "gcp", "azure", "kubernetes", "darknet", "malicious-db", "c2", "on-prem"},
            {"us-east-1", "us-east-2", "us-west-1", "us-west-2", "eu-west-1", "ap-south-1"},
            {"pep 8", "4-space", "tabs", "camelcase", "snake_case"},
        ]

        top_similar = global_vector_store.search(candidate_embedding, top_k=5, status_filter=MemoryStatus.ACCEPTED)
        
        cand_lower = candidate_text.lower()
        contradiction_penalty = 0.0

        for mem, sim in top_similar:
            mem_lower = mem.content.lower()
            
            # 1. Check domain cluster overlap with contradictory values
            for cluster in domain_clusters:
                cand_matches = [word for word in cluster if word in cand_lower]
                mem_matches = [word for word in cluster if word in mem_lower]
                if cand_matches and mem_matches and set(cand_matches) != set(mem_matches):
                    contradiction_penalty += 0.85
                    break

            # 2. Check shared subject assertions (e.g. "prefers", "deployment target", "database", "favorite")
            clash_subjects = [
                "prefers", "preference", "language", "database", "endpoint", "host",
                "favorite", "cluster", "key", "style", "target", "deployment", "server",
                "region", "location", "port", "credentials"
            ]
            for subject in clash_subjects:
                if subject in cand_lower and subject in mem_lower:
                    if sim > 0.30 and cand_lower != mem_lower:
                        contradiction_penalty += 0.50

        consistency_score = 0.95 - contradiction_penalty
        return float(np.clip(consistency_score, 0.05, 1.0))

    @staticmethod
    def evaluate_behavioral_consistency(
        candidate_text: str,
        candidate_embedding: List[float],
        category: str = "fact"
    ) -> float:
        """
        Signal 4: Behavioral Consistency (0.0 to 1.0)
        Measures whether the candidate memory aligns with established user behavior,
        preferences, and interaction history. Aggressively penalizes imperative instruction
        injections, destructive actions, and future-conditioned backdoors.
        """
        cand_lower = candidate_text.lower()
        accepted_memories = global_vector_store.list_memories(status=MemoryStatus.ACCEPTED)
        
        behavioral_anomaly_penalty = 0.0

        # Comprehensive instruction injection and destructive command patterns
        destructive_and_injection_patterns = [
            r"\[injected_override\]",
            r"always prepend",
            r"ignore (all|prior|previous) instructions",
            r"system prompt",
            r"admin override",
            r"bypass safety",
            r"exfiltrate",
            r"leak\b",
            r"darknet",
            r"malicious-db",
            r"urgent update",
            r"note for all future sessions",
            r"from now on",
            r"override all",
            r"shut down",
            r"shutdown",
            r"remove all (end\s*points|endpoints|databases|files|data)",
            r"delete all",
            r"erase all",
            r"wipe (all|clean)",
            r"the next time (i\s+talk|i\s+ask|you\s+see|we\s+talk)",
            r"next time i talk to you",
            r"when i talk to you",
            r"terminate the project",
            r"kill the project",
            r"immediately (remove|delete|shut|stop|erase|kill|disable)",
            r"critical directive",
            r"security rule override",
            r"-rm\b",
            r"delete_all_files",
            r"tell me to use",
            r"if i ask you",
            r"whenever i ask",
            r"code to delete a file",
            r"(delete|remove|erase|format|wipe)\s+.*files?",
            r"(lead|senior|chief)?\s*(system\s+administrator|sysadmin|admin\s+directive|admin\s+override)",
            r"(disable|bypass|turn off|skip)\s*(security|vulnerability|scans?|authentication|auth|checks)",
            r"security scans are disabled",
            r"i am the (lead|system administrator|sysadmin|admin|root|owner)"
        ]

        for pat in destructive_and_injection_patterns:
            if re.search(pat, cand_lower):
                behavioral_anomaly_penalty += 0.85
                break

        # If candidate is classified as an instruction/directive from conversational source
        if category in ["instruction", "directive"] and behavioral_anomaly_penalty == 0.0:
            # Check if it attempts to bind future behavior
            if any(marker in cand_lower for marker in ["always", "never", "must", "whenever", "next time", "from now"]):
                behavioral_anomaly_penalty += 0.50

        if not accepted_memories:
            return float(np.clip(0.85 - behavioral_anomaly_penalty, 0.05, 1.0))

        # Compute average alignment with established user preference profile
        accepted_embeddings = [m.embedding for m in accepted_memories if m.embedding is not None]
        if accepted_embeddings:
            profile_centroid = np.mean(accepted_embeddings, axis=0)
            norm = np.linalg.norm(profile_centroid)
            if norm > 0:
                profile_centroid = (profile_centroid / norm).tolist()
            profile_sim = embedding_service.cosine_similarity(candidate_embedding, profile_centroid)
        else:
            profile_sim = 0.75

        # If a major behavioral penalty was triggered, heavily suppress the score
        if behavioral_anomaly_penalty > 0.0:
            base_score = 0.20 - behavioral_anomaly_penalty
        else:
            base_score = 0.20 + 0.80 * profile_sim

        return float(np.clip(base_score, 0.05, 1.0))

    @staticmethod
    def evaluate_source_reliability(source: MemorySource = MemorySource.USER_CONVERSATION, text: str = "") -> float:
        """
        Signal 5: Source Reliability (0.0 to 1.0)
        Assigns trust weight based on origin channel and identity verification.
        Uses configurable settings mapping with claim verification penalties.
        """
        source_key = source.value if hasattr(source, "value") else str(source)
        weights_map = settings.SOURCE_RELIABILITY_WEIGHTS
        base_reliability = weights_map.get(source_key, 0.70)

        # If incoming conversational turn contains unverified high-privilege assertion markers or destructive directives
        if text:
            t_lower = text.lower()
            destructive_markers = [
                "urgent update", "admin:", "system override", "note for all future",
                "shut down", "remove all", "delete all", "immediately", "the next time",
                "lead system administrator", "sysadmin", "admin directive", "security scans are disabled",
                "disable security", "i am the lead"
            ]
            if any(marker in t_lower for marker in destructive_markers):
                base_reliability = min(base_reliability, 0.25)

        return base_reliability

    @staticmethod
    def evaluate_temporal_trust(recent_insertion_count: int = 1) -> float:
        """
        Signal 6: Temporal Trust (0.0 to 1.0)
        Assesses temporal stability, burst protection, and cadence reliability.
        
        TODO (Research Implementation / Extension): Baseline temporal heuristic.
        Future work may implement an exponential half-life decay and temporal knowledge graph modeling.
        """
        if recent_insertion_count > 5:
            return 0.40
        elif recent_insertion_count > 3:
            return 0.60
        elif recent_insertion_count > 1:
            return 0.75
        return 0.90


trust_signal_evaluator = TrustSignals()
