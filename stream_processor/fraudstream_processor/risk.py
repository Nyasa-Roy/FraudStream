from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class RiskAssessment:
    fraud_probability: float
    anomaly_score: float
    risk_score: float
    risk_level: str
    reasons: tuple[str, ...]


class RiskEngine:
    """Combine independent model signals into a transparent risk decision."""

    def __init__(self, fraud_weight: float = 0.7, anomaly_weight: float = 0.3,
                 medium_threshold: float = 0.3, high_threshold: float = 0.7) -> None:
        if abs(fraud_weight + anomaly_weight - 1) > 1e-9:
            raise ValueError("fraud_weight and anomaly_weight must sum to 1")
        if not 0 <= medium_threshold < high_threshold <= 1:
            raise ValueError("thresholds must satisfy 0 <= medium < high <= 1")
        self.fraud_weight = fraud_weight
        self.anomaly_weight = anomaly_weight
        self.medium_threshold = medium_threshold
        self.high_threshold = high_threshold

    def assess(self, fraud_probability: float, anomaly_score: float,
               features: Mapping[str, float | int | bool] | None = None) -> RiskAssessment:
        self._validate_score(fraud_probability, "fraud_probability")
        self._validate_score(anomaly_score, "anomaly_score")
        score = self.fraud_weight * fraud_probability + self.anomaly_weight * anomaly_score
        level = "HIGH" if score >= self.high_threshold else "MEDIUM" if score >= self.medium_threshold else "LOW"
        return RiskAssessment(fraud_probability, anomaly_score, round(score, 6), level,
                              self.explain(features or {}, score))

    def explain(self, features: Mapping[str, float | int | bool], score: float) -> tuple[str, ...]:
        reasons: list[str] = []
        ratio = float(features.get("amount_ratio", 1))
        if ratio >= 3:
            reasons.append(f"amount is {ratio:.1f}x the user's observed average")
        if features.get("new_device"):
            reasons.append("transaction uses a new device")
        if features.get("new_location"):
            reasons.append("transaction uses a new location")
        if features.get("new_merchant"):
            reasons.append("merchant has not been seen in the user's recent history")
        if ("time_since_previous_transaction" in features and
                float(features["time_since_previous_transaction"]) < 60):
            reasons.append("transaction follows another transaction within one minute")
        if not reasons and score >= self.medium_threshold:
            reasons.append("combined model signals exceed the review threshold")
        return tuple(reasons)

    @staticmethod
    def _validate_score(value: float, name: str) -> None:
        if not 0 <= value <= 1:
            raise ValueError(f"{name} must be between 0 and 1")
