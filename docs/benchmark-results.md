# Runtime benchmark baseline

Measured locally on 2026-08-31 against the Docker Compose API stack using:

```powershell
python benchmarks/run_http_benchmark.py --count 100 --workers 10
```

| Requests | Workers | Throughput | P50 | P95 | P99 | Mean |
|---:|---:|---:|---:|---:|---:|---:|
| 100 | 10 | 22.72 TPS | 369 ms | 681 ms | 1,022 ms | 403 ms |

This is an HTTP API baseline, not the SRS end-to-end Kafka-to-alert benchmark. It exceeds the initial `<500 ms P95` target and establishes the optimization baseline. The initial run also confirmed that invalid benchmark IDs correctly receive HTTP 422 validation responses.

