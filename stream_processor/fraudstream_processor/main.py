from __future__ import annotations

import logging

from backend.fraudstream_backend.repository import PredictionRepository
from fraudstream_ml import InferenceService, train_anomaly_model, train_baseline

from .features import BehaviouralStore, FeatureExtractor
from .worker import TransactionWorker

logging.basicConfig(level=logging.INFO)


def build_worker() -> TransactionWorker:
    """Build the local end-to-end processing pipeline."""
    classifier = train_baseline(count=2_000, fraud_rate=0.05, seed=42)
    anomaly_detector = train_anomaly_model(count=2_000, seed=42)
    inference = InferenceService(classifier, anomaly_detector)
    repository = PredictionRepository()
    extractor = FeatureExtractor(BehaviouralStore())

    def process(transaction, features):
        assessment = inference.predict(transaction, features)
        created = repository.persist(transaction, assessment, classifier.version)
        logging.info("%s risk=%s score=%.3f alert_created=%s", transaction.transaction_id,
                     assessment.risk_level, assessment.risk_score, created)

    return TransactionWorker(process, feature_extractor=extractor)


if __name__ == "__main__":
    build_worker().run()

