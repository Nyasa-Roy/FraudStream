from __future__ import annotations

import json
import os
from typing import Any

from .models import Transaction


class TransactionPublisher:
    """Publish validated transactions to Kafka using transaction IDs as keys."""

    def __init__(self, bootstrap_servers: str | None = None,
                 topic: str | None = None, producer: Any | None = None) -> None:
        self.topic = topic or os.getenv("KAFKA_TRANSACTIONS_TOPIC", "transactions")
        if producer is not None:
            self.producer = producer
            return
        from kafka import KafkaProducer

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers or os.getenv(
                "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
            ),
            key_serializer=lambda value: value.encode("utf-8"),
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
            acks="all",
            retries=5,
        )

    def publish(self, transaction: Transaction) -> Any:
        return self.producer.send(
            self.topic, key=transaction.transaction_id, value=transaction.as_event()
        )

    def flush(self) -> None:
        self.producer.flush()

    def close(self) -> None:
        self.producer.close()
