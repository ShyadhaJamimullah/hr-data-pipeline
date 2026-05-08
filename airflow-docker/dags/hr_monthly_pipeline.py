from airflow import DAG
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args={
    "owner":"airflow",
    "start_date":datetime(2026,3,1),
    "retries":1
}

with DAG(
    dag_id="hr_monthly_pipeline",
    schedule_interval="@monthly",
    catchup=False,
    default_args=default_args,
    template_searchpath=["/opt/airflow/sql"]
) as dag:
    
    aggregate_monthly=MySqlOperator(
        task_id="aggregate_monthly",
        mysql_conn_id="hr_mysql",
        sql="aggregate_monthly.sql"
    )

    aggregate_monthly