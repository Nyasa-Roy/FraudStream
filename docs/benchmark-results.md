# Runtime benchmark baseline

Measured locally on 2026-08-31 against the Docker Compose API stack using:

```powershell
python benchmarks/run_http_benchmark.py --count 100 --workers 10
```

| Requests | Workers | Throughput | P50 | P95 | P99 | Mean |
|---:|---:|---:|---:|---:|---:|---:|
| 100 | 10 | 22.72 TPS | 369 ms | 681 ms | 1,022 ms | 403 ms |

This is an HTTP API baseline, not the SRS end-to-end Kafka-to-alert benchmark. It exceeds the initial `<500 ms P95` target and establishes the optimization baseline. The initial run also confirmed that invalid benchmark IDs correctly receive HTTP 422 validation responses.

## Kafka-to-prediction baseline

Measured against the running Kafka, Redis, PostgreSQL, and stream-processor containers:

| Events | Completed | Throughput | P50 | P95 | P99 |
|---:|---:|---:|---:|---:|---:|
| 20 | 20 | 4.62 TPS | 1,801 ms | 3,976 ms | 4,232 ms |

This baseline includes Kafka publication, consumer processing, Redis feature extraction, model inference, and PostgreSQL prediction persistence. The current serial worker path is above the SRS latency target and is the next optimization target.

## Connection reuse optimization

After reusing one PostgreSQL connection for the worker lifetime, the same 20-event benchmark measured:

| Version | Throughput | P50 | P95 | P99 |
|---|---:|---:|---:|---:|
| Before reuse | 4.62 TPS | 1,801 ms | 3,976 ms | 4,232 ms |
| After reuse | 34.33 TPS | 473 ms | 473 ms | 473 ms |

This is a local development measurement; production capacity still requires larger runs and multi-partition consumers.
