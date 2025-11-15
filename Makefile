.PHONY: help setup start stop logs ingest db ingestion-test clean dbt-run dbt-test dbt-build lint lint-python lint-sql format format-python

help:
	@echo "Available commands:"
	@echo "  make setup          - Install dependencies and start database"
	@echo "  make start          - Start database container"
	@echo "  make stop           - Stop database container"
	@echo "  make logs           - View database logs"
	@echo "  make ingest         - Run data ingestion"
	@echo "  make db             - Connect to database"
	@echo "  make ingestion-test - Run Python ingestion tests"
	@echo "  make dbt-run        - Run dbt models"
	@echo "  make dbt-test       - Run dbt tests"
	@echo "  make dbt-build      - Run dbt models and tests"
	@echo "  make lint           - Lint Python and SQL code"
	@echo "  make lint-python    - Lint Python code only"
	@echo "  make lint-sql       - Lint SQL/dbt code only"
	@echo "  make format         - Format Python code"
	@echo "  make airflow-up     - Start Airflow services"
	@echo "  make airflow-down   - Stop Airflow services"
	@echo "  make airflow-logs   - View Airflow logs"
	@echo "  make clean          - Stop and remove database volumes"

setup:
	@echo "Installing Python dependencies..."
	uv pip install -e ".[dev]"
	@echo "Starting database..."
	docker compose up -d
	@echo "Waiting for database to be ready..."
	@timeout=30; \
	while ! docker compose exec -T postgres pg_isready -U analytics > /dev/null 2>&1; do \
		sleep 1; \
		timeout=$$((timeout-1)); \
		if [ $$timeout -eq 0 ]; then \
			echo "Database failed to start"; \
			exit 1; \
		fi; \
	done
	@echo "Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Copy env.template to .env (if not exists)"
	@echo "  2. Setup dbt profiles: cp dbt/profiles.yml.example ~/.dbt/profiles.yml"
	@echo "  3. Update schema in ~/.dbt/profiles.yml (replace dev_username with your username)"
	@echo "  4. Run: make ingest"
	@echo "  5. Run: make dbt-build"

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

ingestion-test:
	uv run pytest ingestion/tests/ -v

lint: lint-python lint-sql

lint-python:
	uv run ruff check ingestion/
	uv run mypy ingestion/

lint-sql:
	uv run sqlfluff lint dbt/models --dialect postgres

format:
	uv run ruff format ingestion/
	uv run ruff check --fix ingestion/

dbt-run:
	cd dbt && uv run dbt run

dbt-test:
	cd dbt && uv run dbt test

dbt-build:
	cd dbt && uv run dbt build

airflow-up:
	docker compose up -d airflow-webserver airflow-scheduler

airflow-down:
	docker compose stop airflow-webserver airflow-scheduler

airflow-logs:
	docker compose logs -f airflow-webserver airflow-scheduler

clean:
	docker compose down -v
