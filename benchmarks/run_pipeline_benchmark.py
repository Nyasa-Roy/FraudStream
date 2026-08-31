"""Measure Kafka publish-to-prediction completion latency."""

from __future__ import annotations

import argparse
import os
import time
from collections.abc import Iterable

import psycopg

from fraudstream_producer import TransactionGenerator
from fraudstream_producer.publisher import TransactionPublisher


def percentile(values: list[float], percentage: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentage / 100
    lower, upper = int(position), min(int(position) + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def wait_for_predictions(ids: Iterable[str], timeout: float) -> list[float]:
    pending = set(ids)
    started = time.perf_counter()
    completed: list[float] = []
    database_url = os.getenv("DATABASE_URL", "postgresql://fraudstream:fraudstream@localhost:5432/fraudstream")
    with psycopg.connect(database_url) as connection:
        while pending and time.perf_counter() - started < timeout:
            rows = connection.execute(
                "SELECT transaction_id FROM fraud_predictions WHERE transaction_id = ANY(%s)",
                (list(pending),),
            ).fetchall()
            now = time.perf_counter()
            for (transaction_id,) in rows:
                pending.remove(transaction_id)
                completed.append((now - started) * 1000)
            if pending:
                time.sleep(0.05)
    if pending:
        raise TimeoutError(f"{len(pending)} predictions were not persisted within {timeout}s")
    return completed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--timeout", type=float, default=60)
    args = parser.parse_args()
    publisher = TransactionPublisher(bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"))
    ids = []
    started = time.perf_counter()
    for index, transaction in enumerate(TransactionGenerator(fraud_rate=0.2, seed=123).generate(args.count), 90000000):
        event = transaction.model_copy(update={"transaction_id": f"TX{index:08d}"})
        ids.append(event.transaction_id)
        publisher.publish(event)
    publisher.flush()
    latencies = wait_for_predictions(ids, args.timeout)
    elapsed = time.perf_counter() - started
    publisher.close()
    print({"events": args.count, "completed": len(latencies), "throughput_tps": args.count / elapsed,
           "p50_ms": percentile(latencies, 50), "p95_ms": percentile(latencies, 95),
           "p99_ms": percentile(latencies, 99)})


if __name__ == "__main__":
    main()

