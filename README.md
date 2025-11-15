# XKCD Data Platform

A data engineering project for ingesting, transforming, and analyzing XKCD comic data using Python, PostgreSQL, dbt and Airflow.

## Overview

This project implements a complete data pipeline:
- **Ingestion**: Fetches XKCD comics from the public API and loads them into PostgreSQL
- **Transformation**: Uses dbt to create staging and marts layers with Kimball dimensional modeling
- **Analytics**: Calculates business metrics (views, cost, customer reviews) for each comic

## Architecture

```
XKCD API → Python Ingestion → PostgreSQL (raw) → dbt (staging/marts) → Analytics
```

- **Raw Layer**: Stores raw JSON responses from XKCD API
- **Staging Layer**: Parses and normalizes JSON into typed columns
- **Marts Layer**: Kimball star schema with dimension and fact tables

## Prerequisites

- **Docker** and **Docker Compose** (for PostgreSQL)
- **Python 3.12+**
- **uv** (Python package manager) - [Installation guide](https://github.com/astral-sh/uv)
- **dbt** (installed via uv, no separate installation needed)

## Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd jet-project
```

### 2. Setup environment

```bash
# Copy environment template
cp env.template .env

# Setup dbt profiles
mkdir -p ~/.dbt
cp dbt/profiles.yml.example ~/.dbt/profiles.yml

# Edit ~/.dbt/profiles.yml and replace 'dev_username' with your actual username
# This ensures each developer has their own schema
```

### 3. Install and start

```bash
# Install dependencies and start database
make setup
```

### 4. Ingest data

```bash
# Fetch comics from XKCD API and load into database
make ingest
```

### 5. Transform data

```bash
# Run dbt models and tests
make dbt-build
```

## Project Structure

```
.
├── ingestion/          # Python ingestion code
│   ├── extractor.py   # XKCD API client
│   ├── loader.py      # PostgreSQL loader
│   ├── run_ingestion.py
│   └── tests/         # Unit tests
├── dbt/               # dbt transformation project
│   ├── models/
│   │   ├── staging/   # Staging models
│   │   └── marts/     # Dimension and fact tables
│   └── tests/         # Custom data quality tests
├── docker-compose.yml # PostgreSQL service
├── init.sql           # Database initialization
├── Makefile          # Convenient commands
└── pyproject.toml    # Python dependencies
```

## Available Commands

### Database

- `make start` - Start PostgreSQL container
- `make stop` - Stop PostgreSQL container
- `make logs` - View database logs
- `make db` - Connect to database (interactive psql)

### Ingestion

- `make ingest` - Run data ingestion (fetches missing comics)

### Transformation

- `make dbt-run` - Run dbt models
- `make dbt-test` - Run dbt tests
- `make dbt-build` - Run models and tests together

### Testing

- `make ingestion-test` - Run Python ingestion unit tests

### Cleanup

- `make clean` - Stop containers and remove volumes (⚠️ deletes data)

## Data Model

### Raw Layer (`raw.xkcd_comics`)
- Stores raw JSON responses from XKCD API
- Columns: `comic_id`, `raw_json`, `load_ts`, `load_id`

### Staging Layer (`stg_xkcd_comics`)
- Parses JSON into typed columns
- Computes `publish_date` from year/month/day
- Columns: `comic_id`, `title`, `img_url`, `publish_date`, etc.

### Marts Layer

**Dimension Table (`dim_comic`)**
- Comic attributes and metadata
- Includes `title_length` for cost calculation

**Fact Table (`fct_comic_metrics`)**
- Business metrics per comic:
  - `views`: Random number 0-10000
  - `cost_euros`: `title_length * 5` (€5 per letter)
  - `customer_review_score`: Random number 1.0-10.0

## Querying Data

### Connect to database

```bash
make db
```

### Example queries

```sql
-- View raw comics
select count(*) from raw.xkcd_comics;

-- View staging data
select * from <your_schema>_staging.stg_xkcd_comics limit 10;

-- View metrics
select 
    comic_id,
    views,
    cost_euros,
    customer_review_score
from <your_schema>_marts.fct_comic_metrics
order by views desc
limit 10;

-- Join dimension and fact
select 
    d.title,
    d.publish_date,
    f.views,
    f.cost_euros,
    f.customer_review_score
from <your_schema>_marts.dim_comic d
join <your_schema>_marts.fct_comic_metrics f
    on d.comic_id = f.comic_id
order by f.views desc
limit 10;
```

## Development

### Running tests

```bash
# Python ingestion tests
make ingestion-test

# dbt tests
make dbt-test
```

### Code quality

```bash
# Lint all code (Python + SQL)
make lint

# Lint Python code only
make lint-python

# Lint SQL/dbt code only
make lint-sql

# Format Python code
make format
```

## Troubleshooting

### Database connection issues

```bash
# Check if database is running
docker compose ps

# View database logs
make logs

# Restart database
make stop && make start
```

### dbt connection issues

1. Verify `~/.dbt/profiles.yml` exists and has correct credentials
2. Test connection: `cd dbt && uv run dbt debug --profiles-dir ~/.dbt`

### Ingestion fails

- Check internet connection (XKCD API must be accessible)
- Verify `.env` file exists with correct database credentials
- Check database is running: `docker compose ps`

## Multi-Developer Setup

Each developer should:
1. Use their own schema in `~/.dbt/profiles.yml` (e.g., `dev_username`)
2. dbt automatically creates schemas: `<schema>_staging` and `<schema>_marts`
3. No conflicts - each developer has isolated schemas

## Data Quality

The project includes comprehensive data quality tests:
- **Schema tests**: `unique`, `not_null`, `relationships`
- **Custom tests**: Range validation for views and reviews, cost calculation validation

Run all tests: `make dbt-build`

## Next Steps

- Add Airflow DAG for automated scheduling
- Implement polling logic for same-day comic availability
- Add integration tests for full pipeline
- Create ER diagram documentation
