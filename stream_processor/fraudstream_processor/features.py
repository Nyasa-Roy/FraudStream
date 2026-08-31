from __future__ import annotations

import json
import os
from collections.abc import MutableMapping
from datetime import datetime, timezone
from typing import Any

from fraudstream_producer.models import Transaction


class BehaviouralStore:
    """Small Redis adapter that keeps hot user state out of PostgreSQL."""

    def __init__(self, client: Any | None = None) -> None:
        if client is not None:
            self.client = client
            return
        from redis import Redis

        self.client = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                                     decode_responses=True)

    def get(self, user_id: str) -> dict[str, Any]:
        raw = self.client.hgetall(f"user:{user_id}:behaviour")
        if not raw:
            return {"count": 0, "total_amount": 0.0, "last_timestamp": None,
                    "last_location": None, "last_device": None, "merchants": set()}
        state = dict(raw)
        state["count"] = int(state.get("count", 0))
        state["total_amount"] = float(state.get("total_amount", 0))
        state["merchants"] = set(json.loads(state.get("merchants", "[]")))
        return state

    def put(self, user_id: str, state: MutableMapping[str, Any]) -> None:
        payload = dict(state)
        payload["merchants"] = json.dumps(sorted(payload.get("merchants", set())))
        self.client.hset(f"user:{user_id}:behaviour", mapping=payload)


class FeatureExtractor:
    """Calculate transaction and behavioural features, then update user state."""

    def __init__(self, store: BehaviouralStore) -> None:
        self.store = store

    def extract(self, transaction: Transaction) -> dict[str, float | int | bool]:
        state = self.store.get(transaction.user_id)
        count = state["count"]
        average = state["total_amount"] / count if count else 0.0
        timestamp = transaction.timestamp.astimezone(timezone.utc)
        last_timestamp = state.get("last_timestamp")
        elapsed = ((timestamp - datetime.fromisoformat(last_timestamp)).total_seconds()
                   if last_timestamp else 0.0)
        features: dict[str, float | int | bool] = {
            "amount": transaction.amount,
            "amount_log": __import__("math").log1p(transaction.amount),
            "hour": timestamp.hour,
            "day_of_week": timestamp.weekday(),
            "user_average_amount": average,
            "amount_ratio": transaction.amount / average if average else 1.0,
            "transactions_seen": count,
            "new_device": transaction.device_id != state.get("last_device") if count else True,
            "new_location": transaction.location != state.get("last_location") if count else True,
            "new_merchant": transaction.merchant_id not in state["merchants"],
            "time_since_previous_transaction": max(0.0, elapsed),
        }
        self._update(transaction, state, timestamp)
        return features

    def _update(self, transaction: Transaction, state: dict[str, Any], timestamp: datetime) -> None:
        state["count"] += 1
        state["total_amount"] += transaction.amount
        state["last_timestamp"] = timestamp.isoformat()
        state["last_location"] = transaction.location
        state["last_device"] = transaction.device_id
        state["merchants"].add(transaction.merchant_id)
        self.store.put(transaction.user_id, state)

