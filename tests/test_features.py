from datetime import datetime, timezone

from fraudstream_producer import TransactionGenerator
from stream_processor.fraudstream_processor.features import BehaviouralStore, FeatureExtractor


class FakeRedis:
    def __init__(self):
        self.hashes = {}

    def hgetall(self, key):
        return self.hashes.get(key, {}).copy()

    def hset(self, key, mapping):
        self.hashes[key] = {str(k): str(v) for k, v in mapping.items()}


def test_features_use_prior_state_and_update_redis():
    transactions = list(TransactionGenerator(seed=8, start_time=datetime(2026, 1, 1,
        tzinfo=timezone.utc)).generate(2))
    transactions[1] = transactions[1].model_copy(update={"user_id": transactions[0].user_id})
    extractor = FeatureExtractor(BehaviouralStore(FakeRedis()))
    first = extractor.extract(transactions[0])
    second = extractor.extract(transactions[1])
    assert first["transactions_seen"] == 0
    assert second["transactions_seen"] == 1
    assert second["amount_ratio"] > 0
    assert second["time_since_previous_transaction"] >= 0
