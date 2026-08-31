from datetime import datetime, timezone

import pytest

from fraudstream_producer import Transaction, TransactionGenerator


def test_generator_is_reproducible_with_seed() -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    first = list(TransactionGenerator(seed=7, start_time=start).generate(5))
    second = list(TransactionGenerator(seed=7, start_time=start).generate(5))
    assert [item.as_event() for item in first] == [item.as_event() for item in second]


def test_fraud_rate_one_generates_explainable_fraud() -> None:
    transactions = list(TransactionGenerator(fraud_rate=1, seed=3).generate(30))
    assert all(item.is_fraud for item in transactions)
    assert all(item.fraud_pattern for item in transactions)


def test_invalid_transaction_is_rejected() -> None:
    with pytest.raises(ValueError):
        TransactionGenerator(fraud_rate=1.1)
    with pytest.raises(ValueError):
        TransactionGenerator().generate(-1)

