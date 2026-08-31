# FraudStream

FraudStream is a production-style real-time fraud detection platform. It generates synthetic transaction events, enriches them with behavioural features, scores them with ML models, persists decisions, and exposes live monitoring APIs and dashboards.

## Current status

The repository is being implemented incrementally according to the [full SRS](docs/srs.md).

- Phase 0: repository structure and local configuration
- Phase 1: deterministic, configurable synthetic transaction generator
- Phase 2: PostgreSQL schema and local Postgres/Redis services
- Phase 3: FastAPI API for transactions, alerts, analytics, and health
- Next: frontend dashboard and Kafka transport

## Quick start: transaction generator

Requires Python 3.11+.

```powershell
python -m pip install -e ".[dev]"
python -m fraudstream_producer --count 10 --fraud-rate 0.2 --seed 42
```

The command writes newline-delimited JSON to stdout. Use `--output` to write an event file instead.

## Repository layout

```text
backend/          FastAPI service (coming next)
frontend/         Next.js dashboard (coming next)
ml/               Training, evaluation, and model artefacts
producer/         Synthetic transaction event generator
stream_processor/ Kafka consumer and feature pipeline
infrastructure/   Docker Compose and observability configuration
tests/             Unit and integration tests
docs/              Architecture, SRS, API, ML, and operations notes
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for the target event flow and implementation milestones.

## Development

```powershell
pytest
ruff check .
```

Start local persistence services with `docker compose -f infrastructure/docker-compose.yml up -d`.
Run the API with `uvicorn fraudstream_backend.app:app --app-dir backend --reload`.

All data is synthetic; no real payment information is required or stored.
