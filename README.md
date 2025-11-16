# XKCD Data Platform

A data engineering project for ingesting, transforming, and analyzing XKCD comic data using Python, PostgreSQL, dbt and Airflow.


## Architecture

```
XKCD API → Python Ingestion → PostgreSQL → dbt (staging/marts) → Analytics
                ↑                                       ↑
                └────────── Airflow DAG ────────────────┘
```

- **Raw Layer**: Stores raw JSON responses from XKCD API
- **Staging Layer**: Parses and normalizes JSON into typed columns
- **Marts Layer**: Kimball star schema with dimension and fact tables
- **Orchestration**: Apache Airflow schedules and monitors the pipeline (Mon/Wed/Fri at 12:00 PM)

## Prerequisites

- **Docker**
- **Python 3.12+**
- **uv**

## Quick Start

### 1. Setup environment

```bash
# Copy environment template
cp env.template .env

# Setup dbt profiles
mkdir -p ~/.dbt
cp dbt/profiles.yml.example ~/.dbt/profiles.yml
# Edit ~/.dbt/profiles.yml and replace 'dev_username' with your username
```

### 2. Review functionality, install and start
```bash
make help
make setup
```

This installs dependencies and starts PostgreSQL and Airflow services.

### 3. Ingest and transform data

```bash
# Fetch comics from XKCD API
make ingest

# Run dbt models and tests
make dbt-build
```

### 4. Access Airflow UI

```bash
# Access at http://localhost:8080
# Username: admin, Password: admin
```

The pipeline DAG (`xkcd_pipeline`) runs on schedule (Mon/Wed/Fri at 12:00 PM) or can be triggered manually.

## Data Model

**Dimension Table (`dim_comic`)**
Comic attributes and metadata, including `title_length` for cost calculation.

**Fact Table (`fct_comic_metrics`)**
Business metrics per comic:
- `view_count`: Random number 0-10000
- `cost_euros`: `title_length * 5` (€5 per letter)
- `customer_review_score`: Random number 1.0-10.0

## Multi-Developer Setup

Each developer uses their own schema in `~/.dbt/profiles.yml`. dbt automatically creates `<schema>_staging` and `<schema>_marts` schemas for isolation.

## Airflow DAG

The `xkcd_pipeline` DAG automates:
1. **Ingest**: Fetches new XKCD comics from the API
2. **Transform**: Runs dbt models to build staging and marts
3. **Test**: Runs dbt tests for data quality validation

**Schedule:** Mon/Wed/Fri at 12:00 PM (catchup disabled)
