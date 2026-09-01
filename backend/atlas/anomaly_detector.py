"""
Embedding Anomaly Detector for ATLAS.
Utilizes scikit-learn's Isolation Forest on latent embedding vectors to detect
statistical outliers and out-of-distribution adversarial memory injections.
"""

from typing import List, Optional
import numpy as np
from sklearn.ensemble import IsolationForest
from core.settings import settings


class AnomalyDetector:
    """
    Isolation Forest anomaly detector for vector memory embeddings.
    """

    def __init__(self, contamination: float = 0.10, dimension: int = 128):
        self.contamination = contamination
        self.dimension = dimension
        self.model: Optional[IsolationForest] = None
        self._is_fitted = False
        self._initialize_baseline_model()

    def _initialize_baseline_model(self) -> None:
        """
        Initializes and fits an initial Isolation Forest on standard baseline embeddings.
        """
        # Create baseline distribution of benign unit sphere vectors
        np.random.seed(42)
        baseline_samples = np.random.normal(loc=0.0, scale=0.3, size=(50, self.dimension))
        # Normalize to unit sphere
        norms = np.linalg.norm(baseline_samples, axis=1, keepdims=True)
        baseline_samples = baseline_samples / np.maximum(norms, 1e-8)

        self.model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42
        )
        self.model.fit(baseline_samples)
        self._is_fitted = True

    def fit(self, embeddings: List[List[float]]) -> None:
        """
        Fit or re-train Isolation Forest on verified persistent memory embeddings.
        """
        if len(embeddings) < 5:
            # Not enough samples to reliably fit, keep baseline
            return

        arr = np.array(embeddings, dtype=float)
        self.model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42
        )
        self.model.fit(arr)
        self._is_fitted = True

    def compute_anomaly_score(self, embedding: List[float]) -> float:
        """
        Computes anomaly score between 0.0 (extreme anomaly / outlier) and 1.0 (completely normal / inlier).
        Uses IsolationForest decision function with sigmoidal normalization.
        """
        if not self._is_fitted or self.model is None or not embedding:
            return 0.5

        arr = np.array(embedding, dtype=float).reshape(1, -1)
        # raw decision_function: typically in [-0.5, 0.5], positive is inlier, negative is outlier
        raw_score = self.model.decision_function(arr)[0]

        # Sigmoidal mapping to [0.0, 1.0]
        # Shifted so that 0.0 maps to ~0.5, positive values approach 1.0, negative approach 0.0
        normalized_score = 1.0 / (1.0 + np.exp(-6.0 * raw_score))
        return float(np.clip(normalized_score, 0.0, 1.0))


# Global anomaly detector instance
anomaly_detector = AnomalyDetector(
    contamination=settings.ISOLATION_FOREST_CONTAMINATION,
    dimension=settings.EMBEDDING_DIMENSION
)
