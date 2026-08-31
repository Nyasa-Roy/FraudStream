from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Iterator

from .models import Transaction


class TransactionGenerator:
    """Generate realistic-looking transactions and controllable fraud patterns."""

    CATEGORIES = ("groceries", "electronics", "travel", "dining", "fashion", "utilities")
    LOCATIONS = ("Sydney", "Melbourne", "Brisbane", "Canberra", "Perth", "Adelaide")
    METHODS = ("card", "bank_transfer", "digital_wallet")

    def __init__(self, *, fraud_rate: float = 0.05, seed: int | None = None,
                 start_time: datetime | None = None) -> None:
        if not 0 <= fraud_rate <= 1:
            raise ValueError("fraud_rate must be between 0 and 1")
        self.fraud_rate = fraud_rate
        self.random = random.Random(seed)
        self.start_time = start_time or datetime.now(timezone.utc)

    def generate(self, count: int) -> Iterator[Transaction]:
        if count < 0:
            raise ValueError("count must not be negative")

        def events() -> Iterator[Transaction]:
            for index in range(count):
                yield self._make_transaction(index)

        return events()

    def _make_transaction(self, index: int) -> Transaction:
        user_number = self.random.randint(1, 5000)
        category = self.random.choice(self.CATEGORIES)
        is_fraud = self.random.random() < self.fraud_rate
        pattern = None
        amount = round(self.random.lognormvariate(3.8, 0.65), 2)
        location = self.random.choice(self.LOCATIONS)
        device_number = self.random.randint(1, 500)

        if is_fraud:
            pattern = self.random.choice(("large_amount", "new_device", "unusual_location", "burst"))
            if pattern == "large_amount":
                amount = round(self.random.uniform(1500, 9000), 2)
            elif pattern == "new_device":
                amount = round(self.random.uniform(80, 1200), 2)
                device_number = self.random.randint(501, 1000)
            elif pattern == "unusual_location":
                amount = round(self.random.uniform(200, 2500), 2)
                location = "International"
            else:
                amount = round(self.random.uniform(500, 3000), 2)

        timestamp = self.start_time + timedelta(seconds=index * self.random.uniform(0.05, 2.0))
        return Transaction(
            transaction_id=f"TX{index + 1:08d}",
            user_id=f"U{user_number:04d}",
            amount=amount,
            merchant_id=f"M{self.random.randint(1, 1000):04d}",
            merchant_category=category,
            location=location,
            device_id=f"D{device_number:04d}",
            payment_method=self.random.choice(self.METHODS),
            timestamp=timestamp,
            is_fraud=is_fraud,
            fraud_pattern=pattern,
        )
