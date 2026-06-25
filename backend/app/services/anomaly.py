"""Unsupervised anomaly detection — Isolation Forest (Section 4.3 perception layer)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier


class AnomalyDetectionService:
    def __init__(self, contamination: float = 0.05) -> None:
        self.contamination = contamination
        self._isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
        )
        self._classifier: RandomForestClassifier | None = None

    def fit_detect(self, features: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Returns (is_anomaly boolean array, anomaly scores)."""
        if len(features) < 10:
            return np.zeros(len(features), dtype=bool), np.zeros(len(features))

        preds = self._isolation_forest.fit_predict(features)
        scores = -self._isolation_forest.score_samples(features)
        is_anomaly = preds == -1
        return is_anomaly, scores

    def train_classifier(
        self,
        features: np.ndarray,
        labels: np.ndarray,
    ) -> RandomForestClassifier:
        clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        clf.fit(features, labels)
        self._classifier = clf
        return clf

    def predict_known(self, features: np.ndarray) -> np.ndarray | None:
        if self._classifier is None:
            return None
        return self._classifier.predict(features)

    @staticmethod
    def rule_based_baseline(df: pd.DataFrame) -> np.ndarray:
        """Simple threshold monitor for evaluation baseline (Section 4.7)."""
        error_mask = df["level"].isin(["ERROR", "FATAL"])
        long_msg = df["message"].str.len() > 200
        return (error_mask | long_msg).to_numpy()
