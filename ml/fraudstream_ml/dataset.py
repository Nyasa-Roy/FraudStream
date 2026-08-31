from __future__ import annotations

import pandas as pd

from fraudstream_producer import TransactionGenerator


NUMERIC_FEATURES = ("amount", "amount_log", "hour", "day_of_week")
CATEGORICAL_FEATURES = ("merchant_category", "location", "payment_method")
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def build_dataset(count: int = 10_000, fraud_rate: float = 0.05,
                  seed: int = 42) -> tuple[pd.DataFrame, pd.Series]:
    """Build a labelled, synthetic dataset with no real payment information."""
    rows = []
    labels = []
    for transaction in TransactionGenerator(fraud_rate=fraud_rate, seed=seed).generate(count):
        rows.append({
            "amount": transaction.amount,
            "amount_log": __import__("math").log1p(transaction.amount),
            "hour": transaction.timestamp.hour,
            "day_of_week": transaction.timestamp.weekday(),
            "merchant_category": transaction.merchant_category,
            "location": transaction.location,
            "payment_method": transaction.payment_method,
        })
        labels.append(int(transaction.is_fraud))
    return pd.DataFrame(rows, columns=FEATURE_COLUMNS), pd.Series(labels, name="is_fraud")

