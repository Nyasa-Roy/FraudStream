from __future__ import annotations

import pandas as pd

from fraudstream_producer import Transaction
from stream_processor.fraudstream_processor.risk import RiskAssessment, RiskEngine

from .anomaly import AnomalyModel
from .training import BaselineModel


class InferenceService:
    """Run both ML signals and the risk engine for one enriched transaction."""

    def __init__(self, classifier: BaselineModel, anomaly_detector: AnomalyModel,
                 risk_engine: RiskEngine | None = None) -> None:
        self.classifier = classifier
        self.anomaly_detector = anomaly_detector
        self.risk_engine = risk_engine or RiskEngine()

    def predict(self, transaction: Transaction, features: dict) -> RiskAssessment:
        row = pd.DataFrame([{
            "amount": transaction.amount,
            "amount_log": features["amount_log"],
            "hour": features["hour"],
            "day_of_week": features["day_of_week"],
            "merchant_category": transaction.merchant_category,
            "location": transaction.location,
            "payment_method": transaction.payment_method,
        }])
        fraud_probability = self.classifier.predict_probability(row)[0]
        anomaly_score = self.anomaly_detector.score(row)[0]
        return self.risk_engine.assess(fraud_probability, anomaly_score, features)

