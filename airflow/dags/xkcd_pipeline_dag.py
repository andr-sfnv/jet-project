"""XKCD Pipeline DAG."""

from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator


@dag(
    dag_id="xkcd_pipeline",
    description="XKCD comics pipeline",
    schedule="0 12 * * 1,3,5",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["xkcd"],
    default_args={
        "owner": "data-engineering",
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
    },
)
def xkcd_pipeline():
    """XKCD pipeline DAG."""

    @task
    def ingest_xkcd_comics():
        """Run XKCD ingestion."""
        from ingestion.run_ingestion import main

        main()

    dbt_run_task = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run --target airflow --profiles-dir .",
    )

    dbt_test_task = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt && dbt test --target airflow --profiles-dir .",
    )

    ingest_task = ingest_xkcd_comics()
    ingest_task >> dbt_run_task >> dbt_test_task


xkcd_pipeline()

