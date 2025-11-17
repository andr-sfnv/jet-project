.PHONY: help setup start stop logs ingest db ingestion-test clean dbt-run dbt-test dbt-build lint lint-python lint-sql format airflow-trigger

help:
	@echo "Available commands:"
	@echo "  make setup            - Install dependencies and start all services"
	@echo "  make start            - Start all containers"
	@echo "  make stop             - Stop all containers"
	@echo "  make logs             - View all container logs"
	@echo "  make db               - Connect to database"
	@echo "  make ingest           - Run data ingestion"
	@echo "  make ingest-test      - Run Python ingestion tests"
	@echo "  make dbt-run          - Run dbt models"
	@echo "  make dbt-test         - Run dbt tests"
	@echo "  make dbt-build        - Run dbt models and tests"
	@echo "  make lint             - Lint Python and SQL code"
	@echo "  make lint-python      - Lint Python code only"
	@echo "  make lint-sql         - Lint SQL/dbt code only"
	@echo "  make format           - Format Python code"
	@echo "  make clean            - Stop containers, remove volumes, and clear logs"
	@echo "  make airflow-trigger  - Trigger xkcd_pipeline DAG manually"

setup:
	@echo "Installing Python dependencies..."
	uv pip install -e ".[dev]"
	docker compose up -d
	@echo "Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Copy env.template to .env (if not exists)"
	@echo "2. Setup dbt profiles: cp dbt/profiles.yml.example ~/.dbt/profiles.yml"
	@echo "3. Update schema in ~/.dbt/profiles.yml (replace dev_username with your username)"

start:
	docker compose up -d postgres airflow-webserver airflow-scheduler

stop:
	docker compose down

logs:
	docker compose logs -f

db:
	docker compose exec postgres psql -U analytics -d warehouse

ingest:
	uv run python -m ingestion.run_ingestion

ingest-test:
	uv run pytest ingestion/tests/ -v

lint: lint-python lint-sql

lint-python:
	uv run ruff check ingestion/

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

clean:
	docker compose down -v
	rm -rf airflow/logs/dag_id=* airflow/logs/dag_processor airflow/logs/dag_processor_manager airflow/logs/scheduler

airflow-trigger:
	docker compose exec airflow-webserver airflow dags trigger xkcd_pipeline
