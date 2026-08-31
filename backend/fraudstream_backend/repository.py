from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

import psycopg

from fraudstream_producer import Transaction
from stream_processor.fraudstream_processor.risk import RiskAssessment


class PredictionRepository:
    """Persist a processed event and its decision in one database transaction."""

    def __init__(self, connect: Callable[..., Any] | None = None) -> None:
        self.connect = connect or psycopg.connect

    def persist(self, transaction: Transaction, assessment: RiskAssessment,
                model_version: str = "unknown") -> bool:
        """Return True when a new HIGH-risk alert is created."""
        with self.connect(os.getenv(
            "DATABASE_URL", "postgresql://fraudstream:fraudstream@localhost:5432/fraudstream"
        )) as connection:
            connection.execute(
                "INSERT INTO users (id) VALUES (%s) ON CONFLICT (id) DO NOTHING",
                (transaction.user_id,),
            )
            connection.execute(
                """INSERT INTO transactions
                (id, user_id, amount, merchant_id, merchant_category, location,
                 device_id, payment_method, occurred_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING""",
                (transaction.transaction_id, transaction.user_id, transaction.amount,
                 transaction.merchant_id, transaction.merchant_category, transaction.location,
                 transaction.device_id, transaction.payment_method, transaction.timestamp),
            )
            connection.execute(
                """INSERT INTO fraud_predictions
                (transaction_id, model_version, fraud_probability, anomaly_score,
                 risk_score, risk_level, reasons)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (transaction_id) DO UPDATE SET
                  model_version = EXCLUDED.model_version,
                  fraud_probability = EXCLUDED.fraud_probability,
                  anomaly_score = EXCLUDED.anomaly_score,
                  risk_score = EXCLUDED.risk_score,
                  risk_level = EXCLUDED.risk_level,
                  reasons = EXCLUDED.reasons""",
                (transaction.transaction_id, model_version, assessment.fraud_probability,
                 assessment.anomaly_score, assessment.risk_score, assessment.risk_level,
                 __import__("json").dumps(assessment.reasons)),
            )
            if assessment.risk_level != "HIGH":
                return False
            result = connection.execute(
                """INSERT INTO fraud_alerts (transaction_id, risk_score)
                VALUES (%s, %s) ON CONFLICT (transaction_id) DO NOTHING
                RETURNING id""",
                (transaction.transaction_id, assessment.risk_score),
            ).fetchone()
            return result is not None

