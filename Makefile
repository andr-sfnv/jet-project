.PHONY: help setup start stop logs ingest db test clean

help:
	@echo "Commands: setup start stop logs ingest db test clean"

setup:
	uv pip install -e .
	docker compose up -d

start:
	docker compose up -d

stop:
	docker compose down

logs:
	docker compose logs -f postgres

ingest:
	uv run python -m ingestion.run_ingestion

db:
	docker compose exec postgres psql -U analytics -d warehouse

test:
	uv run pytest ingestion/tests/ -v

clean:
	docker compose down -v
