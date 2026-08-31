from __future__ import annotations

import os
from datetime import datetime
from decimal import Decimal
from typing import Any

import psycopg
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://fraudstream:fraudstream@localhost:5432/fraudstream"
)

app = FastAPI(title="FraudStream API", version="0.1.0")


class TransactionInput(BaseModel):
    transaction_id: str = Field(pattern=r"^TX[0-9]+$")
    user_id: str = Field(pattern=r"^U[0-9]+$")
    amount: Decimal = Field(gt=0, le=1_000_000)
    merchant_id: str
    merchant_category: str
    location: str
    device_id: str
    payment_method: str
    timestamp: datetime


def _row_to_dict(row: tuple[Any, ...], columns: tuple[str, ...]) -> dict[str, Any]:
    return dict(zip(columns, row))


@app.get("/health")
def health() -> dict[str, str]:
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=2) as connection:
            connection.execute("SELECT 1")
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ok"}


@app.post("/transactions", status_code=201)
def create_transaction(transaction: TransactionInput) -> dict[str, Any]:
    try:
        with psycopg.connect(DATABASE_URL) as connection:
            connection.execute(
                "INSERT INTO users (id) VALUES (%s) ON CONFLICT (id) DO NOTHING",
                (transaction.user_id,),
            )
            connection.execute(
                """INSERT INTO transactions
                (id, user_id, amount, merchant_id, merchant_category, location,
                 device_id, payment_method, occurred_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (transaction.transaction_id, transaction.user_id, transaction.amount,
                 transaction.merchant_id, transaction.merchant_category, transaction.location,
                 transaction.device_id, transaction.payment_method, transaction.timestamp),
            )
    except psycopg.errors.UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="transaction already exists") from exc
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return transaction.model_dump(mode="json")


@app.get("/transactions")
def list_transactions(limit: int = Query(default=50, ge=1, le=500)) -> list[dict[str, Any]]:
    columns = ("id", "user_id", "amount", "merchant_id", "merchant_category", "location",
               "device_id", "payment_method", "occurred_at", "created_at")
    try:
        with psycopg.connect(DATABASE_URL) as connection:
            rows = connection.execute(
                "SELECT " + ", ".join(columns) +
                " FROM transactions ORDER BY occurred_at DESC LIMIT %s", (limit,)
            ).fetchall()
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return [_row_to_dict(row, columns) for row in rows]


@app.get("/transactions/{transaction_id}")
def get_transaction(transaction_id: str) -> dict[str, Any]:
    columns = ("id", "user_id", "amount", "merchant_id", "merchant_category", "location",
               "device_id", "payment_method", "occurred_at", "created_at")
    try:
        with psycopg.connect(DATABASE_URL) as connection:
            row = connection.execute(
                "SELECT " + ", ".join(columns) +
                " FROM transactions WHERE id = %s", (transaction_id,)
            ).fetchone()
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    if row is None:
        raise HTTPException(status_code=404, detail="transaction not found")
    return _row_to_dict(row, columns)


@app.get("/fraud/alerts")
def list_alerts(limit: int = Query(default=50, ge=1, le=500)) -> list[dict[str, Any]]:
    columns = ("id", "transaction_id", "risk_score", "status", "created_at", "resolved_at")
    try:
        with psycopg.connect(DATABASE_URL) as connection:
            rows = connection.execute(
                "SELECT " + ", ".join(columns) +
                " FROM fraud_alerts ORDER BY created_at DESC LIMIT %s", (limit,)
            ).fetchall()
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return [_row_to_dict(row, columns) for row in rows]


@app.get("/fraud/analytics")
def fraud_analytics() -> dict[str, Any]:
    try:
        with psycopg.connect(DATABASE_URL) as connection:
            total = connection.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
            alerts = connection.execute("SELECT COUNT(*) FROM fraud_alerts").fetchone()[0]
            levels = connection.execute(
                "SELECT risk_level, COUNT(*) FROM fraud_predictions GROUP BY risk_level"
            ).fetchall()
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"transaction_count": total, "alert_count": alerts,
            "risk_distribution": {level: count for level, count in levels}}

