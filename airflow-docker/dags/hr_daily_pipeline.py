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
    
    generate_csv=BashOperator(
        task_id="generate_csv",
        bash_command="python /opt/airflow/scripts/generate_daily_snapshot.py {{ds}}"
    )

    create_tables=MySqlOperator(
        task_id="create_tables",
        mysql_conn_id="hr_mysql",
        sql="create_tables.sql"
    )


    load_raw=MySqlOperator(
        task_id="load_csv",
        mysql_conn_id="hr_mysql",
        sql="""
        LOAD DATA INFILE '/var/lib/mysql-files/snapshot_{{ ds_nodash }}.csv'
        INTO TABLE hr_transactions_raw
        FIELDS TERMINATED BY ','
        IGNORE 1 ROWS;
        """
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

    create_tables >> generate_csv >> load_raw >> prepare_staging >> transform_daily 
    
    


  
    
    


