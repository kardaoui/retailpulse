"""DAG principal RetailPulse : ingestion → validation → transformation → notification."""

import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

logger = logging.getLogger(__name__)

default_args = {
    "owner": "retailpulse",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=30),
}

with DAG(
    dag_id="retailpulse_dag",
    description="Pipeline e-commerce Olist : CSV → GE → dbt staging → dbt mart",
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["retailpulse", "portfolio"],
) as dag:

    ingest_olist_csv = BashOperator(
        task_id="ingest_olist_csv",
        bash_command="python /opt/airflow/ingestion/load_olist.py",
    )

    run_great_expectations = BashOperator(
        task_id="run_great_expectations",
        bash_command=(
            "cd /opt/great_expectations && "
            "great_expectations checkpoint run olist_checkpoint"
        ),
    )

    dbt_run_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command="dbt run --project-dir /opt/dbt --profiles-dir /opt/dbt --select staging",
    )

    dbt_run_mart = BashOperator(
        task_id="dbt_run_mart",
        bash_command="dbt run --project-dir /opt/dbt --profiles-dir /opt/dbt --select mart",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="dbt test --project-dir /opt/dbt --profiles-dir /opt/dbt",
    )

    def _notify_success(**context):
        logger.info(
            "Pipeline RetailPulse terminé avec succès — date d'exécution : %s",
            context["ds"],
        )

    notify_success = PythonOperator(
        task_id="notify_success",
        python_callable=_notify_success,
    )

    # Ordre d'exécution
    ingest_olist_csv >> run_great_expectations >> dbt_run_staging >> dbt_run_mart >> dbt_test >> notify_success
