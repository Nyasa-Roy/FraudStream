from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUESTS = Counter("fraudstream_http_requests_total", "HTTP requests", ["method", "path", "status"])
LATENCY = Histogram("fraudstream_http_request_duration_seconds", "HTTP request latency", ["method", "path"])
TRANSACTIONS = Counter("fraudstream_transactions_total", "Transactions accepted by the API")
ALERTS = Counter("fraudstream_alerts_total", "Fraud alerts created", ["risk_level"])


def metrics_payload() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST

