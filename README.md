# HR Data Pipeline

A local, Docker-based data engineering project that simulates daily employee snapshots and turns them into analytics-ready HR fact and dimension tables.

Apache Airflow orchestrates the workflow, Kafka transports snapshot events, MySQL stores the HR data, and SQL transformations build daily and monthly analytical models.

## Architecture

```text
Employee master CSV
        |
        v
Daily snapshot generator
        |
        v
Kafka producer --> hr_daily_snapshot_events --> Kafka consumer
                                                  |
                                                  v
                                      hr_transactions_raw
                                                  |
                                                  v
                                      hr_transactions_staging
                                                  |
                                                  v
                              dimensions + fact_hr_daily
                                                  |
                                                  v
                                         fact_hr_monthly
```

Airflow uses PostgreSQL for its metadata database and Redis as the Celery message broker. These are separate from MySQL, which stores the HR pipeline data.

## Pipeline workflows

### Daily pipeline

The `hr_daily_pipeline` DAG runs daily and performs these tasks in order:

1. Creates the MySQL tables if they do not exist.
2. Generates `snapshot_YYYYMMDD.csv` from the employee master.
3. publishes one Kafka event per employee.
4. Consumes events for the requested snapshot date into `hr_transactions_raw`.
5. Refreshes that date in `hr_transactions_staging`.
6. Loads dimensions and the daily fact table.

Daily transformations derive income bands, tenure, tenure bands, and a numeric relieved flag.

### Monthly pipeline

The `hr_monthly_pipeline` DAG runs monthly and aggregates `fact_hr_daily` into `fact_hr_monthly` by year, month, and department. It calculates:

- Total employees
- Average salary
- Attrition count and rate
- Overtime rate
- Average tenure

Both DAGs have `catchup=False`, start from March 1, 2026, and are paused when first created by the current Docker configuration.

## Technology stack

- Apache Airflow 2.8.1 with CeleryExecutor
- Apache Kafka 7.5.0 and ZooKeeper
- MySQL 8.0
- PostgreSQL 13 and Redis
- Python, pandas, Faker, and kafka-python
- Docker Compose

## Project structure

```text
hr_data_pipeline/
|-- airflow-docker/
|   |-- dags/
|   |   |-- hr_daily_pipeline.py
|   |   `-- hr_monthly_pipeline.py
|   |-- Dockerfile
|   |-- docker-compose.yaml
|   `-- requirements.txt
|-- scripts/
|   |-- create_employee_master.py
|   |-- generate_daily_snapshot.py
|   |-- kafka_producer_snapshot.py
|   `-- kafka_consumer_to_mysql.py
|-- sql/
|   |-- create_tables.sql
|   |-- transform_daily.sql
|   `-- aggregate_monthly.sql
`-- README.md
```

Generated CSV files live in `data/`, and Airflow runtime logs live in `airflow-docker/logs/`. Both locations are excluded from Git.

## Prerequisites

- Docker Desktop with Docker Compose
- At least 4 GB of memory available to Docker; 8 GB is more comfortable for the full stack
- Ports `8080`, `9092`, `2181`, and `3307` available on the host

## Getting started

### 1. Configure local environment variables

Create `airflow-docker/.env`:

```dotenv
AIRFLOW_UID=50000
POSTGRES_PASSWORD=airflow
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=hr_db
MYSQL_PORT=3307
```

These values are suitable only for local development. The current DAG passes `root` to the Kafka consumer, so `MYSQL_ROOT_PASSWORD` must match it unless the DAG is changed to use a different secret-management approach.

### 2. Build and initialize Airflow

From the repository root:

```powershell
docker compose -f airflow-docker/docker-compose.yaml build
docker compose -f airflow-docker/docker-compose.yaml up airflow-init
```

### 3. Start the services

```powershell
docker compose -f airflow-docker/docker-compose.yaml up -d
```

Open the Airflow UI at [http://localhost:8080](http://localhost:8080). The local default login is `airflow` / `airflow` unless it is overridden in `.env`.

### 4. Create the Airflow MySQL connection

In the Airflow UI, open **Admin > Connections**, add a connection, and use:

| Field | Value |
|---|---|
| Connection ID | `hr_mysql` |
| Connection type | `MySQL` |
| Host | `mysql` |
| Database/Schema | `hr_db` |
| Login | `root` |
| Password | The value of `MYSQL_ROOT_PASSWORD` |
| Port | `3306` |

The port is `3306` inside the Docker network even though MySQL is exposed as `3307` on the host by default.

### 5. Generate the employee master

The daily DAG expects `/opt/airflow/data/employee_master.csv`. Generate the initial 500-record file once:

```powershell
docker compose -f airflow-docker/docker-compose.yaml exec airflow-scheduler python /opt/airflow/scripts/create_employee_master.py
```

### 6. Run the pipelines

In the Airflow UI:

1. Unpause `hr_daily_pipeline`.
2. Trigger it or wait for its daily schedule.
3. After daily fact data exists, unpause and trigger `hr_monthly_pipeline`.

The daily DAG passes its Airflow logical date (`YYYY-MM-DD`) through the CSV generator, Kafka producer, Kafka consumer, staging refresh, and SQL transformation steps.

## Data model

| Layer | Table | Purpose |
|---|---|---|
| Raw | `hr_transactions_raw` | Kafka-consumed employee snapshot events |
| Staging | `hr_transactions_staging` | Date-scoped input to transformations |
| Dimension | `dim_employee` | Employee identity and employment attributes |
| Dimension | `dim_department` | Unique department names and generated IDs |
| Dimension | `dim_date` | Calendar fields for each snapshot date |
| Fact | `fact_hr_daily` | Employee-level daily HR metrics |
| Fact | `fact_hr_monthly` | Monthly department-level HR aggregates |

The daily fact table uses `(EmployeeID, SnapshotDate)` as its primary key. The monthly fact table uses `(Year, Month, DepartmentID)`.

## Useful commands

View service status:

```powershell
docker compose -f airflow-docker/docker-compose.yaml ps
```

Follow Airflow scheduler logs:

```powershell
docker compose -f airflow-docker/docker-compose.yaml logs -f airflow-scheduler
```

Follow Kafka or MySQL logs:

```powershell
docker compose -f airflow-docker/docker-compose.yaml logs -f kafka
docker compose -f airflow-docker/docker-compose.yaml logs -f mysql
```

Open a MySQL shell:

```powershell
docker compose -f airflow-docker/docker-compose.yaml exec mysql mysql -uroot -p hr_db
```

Stop the stack without deleting persisted data:

```powershell
docker compose -f airflow-docker/docker-compose.yaml down
```


