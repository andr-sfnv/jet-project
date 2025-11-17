"""XKCD Pipeline DAG."""

from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.sensors.python import PythonSensor

SENSOR_TIMEOUT_SECONDS = 43200  # 12 hours
SENSOR_POKE_INTERVAL_SECONDS = 300  # 5 minutes


@dag(
    dag_id="xkcd_pipeline",
    description="XKCD comics pipeline",
    schedule="0 12 * * 1,3,5",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["xkcd"],
    is_paused_upon_creation=False,
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

    @task.branch
    def sensor_branch(**context):
        """Skip sensor for manual triggers, otherwise wait for new comic."""
        from ingestion.poller import should_skip_sensor

        return should_skip_sensor(**context)

    def check_new_comic_callable():
        """Check if a new comic is available (delayed import for sensor)."""
        from ingestion.poller import check_new_comic_available

        return check_new_comic_available()

    wait_for_new_comic_task = PythonSensor(
        task_id="wait_for_new_comic",
        python_callable=check_new_comic_callable,
        mode="reschedule",
        poke_interval=SENSOR_POKE_INTERVAL_SECONDS,
        exponential_backoff=True,
        timeout=SENSOR_TIMEOUT_SECONDS,
    )

    skip_sensor_task = EmptyOperator(task_id="skip_sensor")

    @task()
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
    sensor_branch_task = sensor_branch()

    sensor_branch_task >> [wait_for_new_comic_task, skip_sensor_task] >> ingest_task
    ingest_task >> dbt_run_task >> dbt_test_task


xkcd_pipeline()

