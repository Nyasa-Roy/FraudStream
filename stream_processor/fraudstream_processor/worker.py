from __future__ import annotations

import json
import logging
import os
import time
from collections.abc import Callable
from typing import Any

from pydantic import ValidationError

from fraudstream_producer.models import Transaction

logger = logging.getLogger(__name__)


class TransactionWorker:
    """Consume transaction events and hand validated messages to a processor.

    Invalid payloads are acknowledged and logged because retrying malformed data
    forever would block a Kafka partition. Transient processor failures are retried
    with bounded exponential backoff before the message is acknowledged.
    """

    def __init__(self, processor: Callable[..., None], consumer: Any | None = None,
                 feature_extractor: Any | None = None,
                 *, max_retries: int = 3, base_backoff: float = 0.1) -> None:
        self.processor = processor
        self.feature_extractor = feature_extractor
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        if consumer is not None:
            self.consumer = consumer
            return
        from kafka import KafkaConsumer

        self.consumer = KafkaConsumer(
            os.getenv("KAFKA_TRANSACTIONS_TOPIC", "transactions"),
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            group_id=os.getenv("KAFKA_GROUP_ID", "fraudstream-processor"),
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        )

    def handle(self, message: Any) -> bool:
        try:
            transaction = Transaction.model_validate(message.value)
        except (ValidationError, TypeError, ValueError) as exc:
            logger.error("Dropping invalid transaction event: %s", exc)
            self.consumer.commit()
            return False

        for attempt in range(self.max_retries + 1):
            try:
                features = (self.feature_extractor.extract(transaction)
                            if self.feature_extractor else None)
                if features is None:
                    self.processor(transaction)
                else:
                    self.processor(transaction, features)
                self.consumer.commit()
                return True
            except Exception:
                if attempt == self.max_retries:
                    logger.exception("Transaction processing failed after retries")
                    self.consumer.commit()
                    return False
                time.sleep(self.base_backoff * (2 ** attempt))
        return False

    def run(self) -> None:
        for message in self.consumer:
            self.handle(message)
