.PHONY: help setup start stop logs ingest db ingestion-test clean dbt-run dbt-test dbt-build lint lint-python lint-sql format airflow-init airflow-up airflow-down airflow-logs

help:
	@echo "Available commands:"
	@echo "  make setup          - Install dependencies and start all services"
	@echo "  make start          - Start all containers"
	@echo "  make stop           - Stop all containers"
	@echo "  make logs           - View all container logs"
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
	@echo "  make airflow-init   - Initialize Airflow database"
	@echo "  make airflow-up     - Start Airflow services"
	@echo "  make airflow-down   - Stop Airflow services"
	@echo "  make airflow-logs   - View Airflow logs"
	@echo "  make clean          - Stop containers, remove volumes, and clear logs"

setup:
	@echo "Installing Python dependencies..."
	uv pip install -e ".[dev]"
	docker compose up -d postgres
	docker compose up airflow-init
	docker compose up -d airflow-webserver airflow-scheduler
	@echo "Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Copy env.template to .env (if not exists)"
	@echo "  2. Setup dbt profiles: cp dbt/profiles.yml.example ~/.dbt/profiles.yml"
	@echo "  3. Update schema in ~/.dbt/profiles.yml (replace dev_username with your username)"

start:
	docker compose up -d

stop:
	docker compose down

logs:
	docker compose logs -f

ingest:
	uv run python -m ingestion.run_ingestion

db:
	docker compose exec postgres psql -U analytics -d warehouse

ingestion-test:
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

airflow-init:
	docker compose up airflow-init

airflow-up: airflow-init
	docker compose up -d airflow-webserver airflow-scheduler

airflow-down:
	docker compose stop airflow-webserver airflow-scheduler

airflow-logs:
	docker compose logs -f airflow-webserver airflow-scheduler

clean:
	docker compose down -v
	rm -rf airflow/logs/dag_id=* airflow/logs/dag_processor airflow/logs/dag_processor_manager airflow/logs/scheduler
