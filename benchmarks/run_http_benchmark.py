"""Small dependency-free benchmark for the running FraudStream API."""

from __future__ import annotations

import argparse
import json
import statistics
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor


def post_transaction(base_url: str, index: int) -> float:
    payload = json.dumps({"transaction_id": f"TX{900000000 + index:09d}", "user_id": "U0001",
        "amount": 42.50, "merchant_id": "M0001", "merchant_category": "groceries",
        "location": "Sydney", "device_id": "D0001", "payment_method": "card",
        "timestamp": "2026-01-01T00:00:00Z"}).encode()
    request = urllib.request.Request(f"{base_url}/transactions", data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=10):
        pass
    return (time.perf_counter() - started) * 1000


def percentile(values: list[float], percentage: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentage / 100
    lower, upper = int(position), min(int(position) + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args()
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        latencies = list(pool.map(lambda i: post_transaction(args.base_url, i), range(args.count)))
    elapsed = time.perf_counter() - started
    print(json.dumps({"requests": args.count, "throughput_tps": args.count / elapsed,
        "p50_ms": percentile(latencies, 50), "p95_ms": percentile(latencies, 95),
        "p99_ms": percentile(latencies, 99), "mean_ms": statistics.mean(latencies)}, indent=2))


if __name__ == "__main__":
    main()
