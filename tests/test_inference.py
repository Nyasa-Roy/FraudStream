from datetime import datetime, timezone

from fraudstream_ml import InferenceService, train_anomaly_model, train_baseline
from fraudstream_producer import TransactionGenerator
from stream_processor.fraudstream_processor.features import BehaviouralStore, FeatureExtractor


def test_inference_combines_classifier_anomaly_and_explanations():
    classifier = train_baseline(400, fraud_rate=0.2, seed=21)
    anomaly = train_anomaly_model(400, seed=21)
    transaction = next(TransactionGenerator(seed=22, start_time=datetime(2026, 1, 1,
        tzinfo=timezone.utc)).generate(1))
    features = FeatureExtractor(BehaviouralStore(_FakeRedis())).extract(transaction)
    result = InferenceService(classifier, anomaly).predict(transaction, features)
    assert 0 <= result.fraud_probability <= 1
    assert 0 <= result.anomaly_score <= 1
    assert 0 <= result.risk_score <= 1
    assert result.risk_level in {"LOW", "MEDIUM", "HIGH"}


class _FakeRedis:
    def __init__(self):
        self.data = {}

    def hgetall(self, key):
        return self.data.get(key, {}).copy()

    def hset(self, key, mapping):
        self.data[key] = {str(k): str(v) for k, v in mapping.items()}

