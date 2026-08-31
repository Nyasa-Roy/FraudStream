from datetime import datetime, timezone

from backend.fraudstream_backend.repository import PredictionRepository
from fraudstream_producer import TransactionGenerator
from stream_processor.fraudstream_processor.risk import RiskEngine


class FakeConnection:
    def __init__(self):
        self.calls = []
        self.alert_result = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, query, params=()):
        self.calls.append((query, params))
        return self

    def fetchone(self):
        return self.alert_result


def make_repository():
    connection = FakeConnection()
    return PredictionRepository(connect=lambda _: connection), connection


def test_persists_prediction_without_alert_for_low_risk():
    transaction = next(TransactionGenerator(seed=31, start_time=datetime(2026, 1, 1,
        tzinfo=timezone.utc)).generate(1))
    repository, connection = make_repository()
    assessment = RiskEngine().assess(0.1, 0.2, {})
    assert repository.persist(transaction, assessment, "test-v1") is False
    assert len(connection.calls) == 3
    assert "fraud_predictions" in connection.calls[2][0]


def test_creates_alert_for_high_risk():
    transaction = next(TransactionGenerator(seed=31).generate(1))
    repository, connection = make_repository()
    connection.alert_result = (17,)
    assessment = RiskEngine().assess(0.95, 0.9, {"amount_ratio": 12})
    assert repository.persist(transaction, assessment) is True
    assert "fraud_alerts" in connection.calls[-1][0]

