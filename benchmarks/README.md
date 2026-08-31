# Benchmarks

Start the local stack, then run:

```powershell
python benchmarks/run_http_benchmark.py --count 1000 --workers 25
```

The runner reports measured throughput and P50/P95/P99 request latency. It does not claim end-to-end Kafka latency; that benchmark will be added once the consumer persistence path is wired into the running Compose stack.

