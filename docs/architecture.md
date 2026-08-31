# Architecture

```mermaid
flowchart LR
  G[Transaction generator] --> K[(Kafka: transactions)]
  K --> W[Stream processor]
  W --> R[(Redis behavioural state)]
  W --> M[ML inference]
  M --> E[Risk engine]
  E --> P[(PostgreSQL)]
  E --> A[(Kafka: fraud-alerts)]
  A --> S[WebSocket/API service]
  S --> D[Dashboard]
```

The first increment deliberately keeps generation independent of Kafka. This makes the event contract testable and provides deterministic JSONL fixtures before infrastructure is introduced.

