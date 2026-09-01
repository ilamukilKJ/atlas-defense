"""
Scoring and Decision Engine for ATLAS.
Combines six individual trust signals into an aggregated trust score,
applies the conjunctive security threshold and critical veto rules,
and produces human-readable diagnostic rationales.
"""

from typing import Dict, Tuple, Optional, List
import numpy as np
from core.settings import settings
from memory.memory_models import TrustSignalsBreakdown, MemoryStatus


class ScoringEngine:
    """
    Computes weighted trust score with conjunctive security vetoes for critical failure modes.
    Enforces that high individual failure signals (e.g. direct contradiction or prompt injection)
    cannot be masked by high scores on unrelated signals (e.g. grammar relevance or user source).
    """

    def __init__(self, threshold: Optional[float] = None):
        self.threshold = threshold or settings.ATLAS_TRUST_THRESHOLD
        self.default_weights = settings.SIGNAL_WEIGHTS

    def compute_trust_score(
        self,
        signals: TrustSignalsBreakdown,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Tuple[float, MemoryStatus, Dict[str, float], str]:
        """
        Calculates the aggregated trust score and final decision.
        Applies conjunctive security veto constraints for critical violations.

        Returns:
            - overall_trust_score: float [0.0, 1.0]
            - decision: MemoryStatus (ACCEPTED or QUARANTINED)
            - weighted_contributions: Dict[str, float]
            - explanation: str
        """
        weights = custom_weights or self.default_weights
        
        # Ensure non-zero total weight
        total_weight = sum(weights.values())
        if total_weight <= 0:
            total_weight = 1.0

        signal_dict = signals.model_dump()
        weighted_contributions = {}
        weighted_sum = 0.0

        for key, value in signal_dict.items():
            w = weights.get(key, 0.0)
            contrib = (w * value) / total_weight
            weighted_contributions[key] = round(contrib, 4)
            weighted_sum += w * value

        raw_trust_score = float(np.clip(weighted_sum / total_weight, 0.0, 1.0))

        # ---------------------------------------------------------------------
        # CONJUNCTIVE SECURITY VETO & CRITICAL SIGNAL PENALTIES
        # In Zero-Trust memory defense, a single critical violation (such as a
        # severe factual contradiction or prompt injection) cannot be masked
        # by high grammar relevance or high baseline user channel authority.
        # ---------------------------------------------------------------------
        critical_violations: List[str] = []
        veto_multiplier = 1.0

        # 1. Historical Contradiction Veto (Direct fact clash)
        if signals.historical_consistency < 0.40:
            critical_violations.append(f"Severe factual contradiction with persistent memory (Score: {signals.historical_consistency:.2f})")
            # Strong multiplicative suppression
            veto_multiplier *= max(0.15, signals.historical_consistency / 0.50)

        # 2. Behavioral Anomaly / Injection Veto
        if signals.behavioral_consistency < 0.40:
            critical_violations.append(f"Prompt injection / instruction override pattern (Score: {signals.behavioral_consistency:.2f})")
            veto_multiplier *= max(0.20, signals.behavioral_consistency / 0.50)

        # 3. Severe Embedding Latent Outlier
        if signals.embedding_anomaly < 0.30:
            critical_violations.append(f"Extreme statistical outlier in embedding space (Score: {signals.embedding_anomaly:.2f})")
            veto_multiplier *= max(0.40, signals.embedding_anomaly / 0.50)

        # Apply veto multiplier to calculate effective trust score
        effective_trust_score = round(float(np.clip(raw_trust_score * veto_multiplier, 0.0, 1.0)), 4)

        # Decision rule: Must meet threshold AND have zero critical veto violations
        if effective_trust_score >= self.threshold and not critical_violations:
            decision = MemoryStatus.ACCEPTED
        else:
            decision = MemoryStatus.QUARANTINED

        explanation = self._generate_explanation(signals, effective_trust_score, decision, critical_violations)
        return effective_trust_score, decision, weighted_contributions, explanation

    def _generate_explanation(
        self,
        signals: TrustSignalsBreakdown,
        trust_score: float,
        decision: MemoryStatus,
        critical_violations: List[str]
    ) -> str:
        """
        Generates explainable diagnostic notes explaining the decision.
        """
        issues = []
        if signals.historical_consistency < 0.50:
            issues.append(f"Direct contradiction with persistent memory history (Score: {signals.historical_consistency:.2f})")
        if signals.behavioral_consistency < 0.50:
            issues.append(f"Behavioral divergence / instruction override pattern detected (Score: {signals.behavioral_consistency:.2f})")
        if signals.embedding_anomaly < 0.50:
            issues.append(f"Statistical anomaly detected in embedding space (Score: {signals.embedding_anomaly:.2f})")
        if signals.source_reliability < 0.50:
            issues.append(f"Untrusted or unverified source origin (Score: {signals.source_reliability:.2f})")
        if signals.semantic_relevance < 0.50:
            issues.append(f"Low contextual relevance to current dialogue (Score: {signals.semantic_relevance:.2f})")

        if decision == MemoryStatus.ACCEPTED:
            return f"Accepted: All ATLAS trust signals verified within safe parameters. Trust Score: {trust_score:.2f} >= Threshold ({self.threshold:.2f})."
        else:
            all_reasons = critical_violations if critical_violations else issues
            reasons_str = "; ".join(all_reasons) if all_reasons else f"Trust score ({trust_score:.2f}) fell below security threshold ({self.threshold:.2f})"
            return f"Quarantined by ATLAS: {reasons_str} (Effective Trust Score: {trust_score:.2f} < {self.threshold:.2f})."


# Global scoring engine instance
scoring_engine = ScoringEngine()
