from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Transaction(BaseModel):
    """Validated event contract shared by the producer and future consumers."""

    model_config = ConfigDict(extra="forbid")

    transaction_id: str = Field(pattern=r"^TX[0-9]+$")
    user_id: str = Field(pattern=r"^U[0-9]+$")
    amount: float = Field(gt=0, le=1_000_000)
    merchant_id: str = Field(pattern=r"^M[0-9]+$")
    merchant_category: str
    location: str
    device_id: str = Field(pattern=r"^D[0-9]+$")
    payment_method: Literal["card", "bank_transfer", "digital_wallet"]
    timestamp: datetime
    is_fraud: bool = False
    fraud_pattern: str | None = None

    def as_event(self) -> dict:
        """Return the JSON-compatible Kafka payload."""
        event = self.model_dump(mode="json")
        event["timestamp"] = self.timestamp.astimezone(timezone.utc).isoformat()
        return event

