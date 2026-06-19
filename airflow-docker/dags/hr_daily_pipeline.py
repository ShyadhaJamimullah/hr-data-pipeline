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
    dag_id="hr_daily_pipeline",
    schedule_interval="@daily",
    catchup=False,
    #max_active_runs=1,
    default_args=default_args,
    template_searchpath=["/opt/airflow/sql"]
) as dag:
    


    create_tables=MySqlOperator(
        task_id="create_tables",
        mysql_conn_id="hr_mysql",
        sql="create_tables.sql"
    )

    generate_csv=BashOperator(
        task_id="generate_csv",
        bash_command="python /opt/airflow/scripts/generate_daily_snapshot.py {{ds}}"
    )

    send_to_kafka = BashOperator(
        task_id="send_to_kafka",
        bash_command="python /opt/airflow/scripts/kafka_producer_snapshot.py {{ ds }}"
    )

    consume_from_kafka = BashOperator(
        task_id="consume_from_kafka",
        bash_command="python /opt/airflow/scripts/kafka_consumer_to_mysql.py {{ ds }}",
        env={
            "MYSQL_ROOT_PASSWORD": "root",
            "MYSQL_DATABASE": "hr_db"
        }
    )


    prepare_staging=MySqlOperator(
        task_id="prepare_staging",
        mysql_conn_id="hr_mysql",
        sql="""
        DELETE FROM hr_transactions_staging WHERE SnapshotDate='{{ds}}';

        INSERT INTO hr_transactions_staging
        SELECT *
        FROM hr_transactions_raw
        WHERE SnapshotDate='{{ ds }}';
        """
    )

    transform_daily=MySqlOperator(
        task_id="transform_daily",
        mysql_conn_id="hr_mysql",
        sql="transform_daily.sql"
    )

    create_tables >> generate_csv >> send_to_kafka >> consume_from_kafka >> prepare_staging >> transform_daily 
    
    


  
    
    


