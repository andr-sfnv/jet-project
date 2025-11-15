"""XKCD Pipeline DAG."""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from ingestion.run_ingestion import main as ingest_main


def ingest_xkcd_data():
    """Run XKCD ingestion."""
    ingest_main()


default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "start_date": datetime(2025, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "xkcd_etl_pipeline",
    default_args=default_args,
    description="XKCD comics ETL pipeline",
    schedule="0 12 * * 1,3,5",
    catchup=False,
    tags=["xkcd", "etl"],
)

ingest_task = PythonOperator(
    task_id="ingest_xkcd_comics",
    python_callable=ingest_xkcd_data,
    dag=dag,
)

dbt_run_task = BashOperator(
    task_id="dbt_run",
    bash_command="cp /opt/airflow/dbt/profiles.yml.airflow /opt/airflow/dbt/profiles.yml && cd /opt/airflow/dbt && dbt run",
    dag=dag,
)

dbt_test_task = BashOperator(
    task_id="dbt_test",
    bash_command="cd /opt/airflow/dbt && dbt test",
    dag=dag,
)

ingest_task >> dbt_run_task >> dbt_test_task

