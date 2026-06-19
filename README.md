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

Open a terminal in the `airflow-docker` folder. From the repository root, you can enter it with:

```powershell
cd airflow-docker
```

Run all Docker Compose commands below from this directory.

### Normal use

After the project has been initialized once, start the complete pipeline stack with:

```powershell
docker compose up -d
```

Then:

1. Open the Airflow UI at [http://localhost:8080](http://localhost:8080).
2. Sign in with your configured Airflow credentials.
3. Unpause `hr_daily_pipeline` if it is paused.
4. Trigger `hr_daily_pipeline` from the UI.
5. Trigger `hr_monthly_pipeline` after daily fact data exists when you want to refresh the monthly aggregates.

### First-time setup

#### 1. Configure local environment variables

Create `.env` inside the `airflow-docker` directory:

```dotenv
AIRFLOW_UID=50000
POSTGRES_PASSWORD=<choose-a-password>
MYSQL_ROOT_PASSWORD=<choose-a-password>
MYSQL_DATABASE=hr_db
MYSQL_PORT=3307
```

These values are suitable only for local development. The current DAG passes `root` to the Kafka consumer, so `MYSQL_ROOT_PASSWORD` must match it unless the DAG is changed to use a different secret-management approach.

#### 2. Build and initialize Airflow

```powershell
docker compose build
docker compose up airflow-init
```

Start the services after initialization:

```powershell
docker compose up -d
```

The local default Airflow login is `airflow` / `airflow` unless it is overridden in `.env`.

#### 3. Create the Airflow MySQL connection

You only need to create the Airflow connection named `hr_mysql`. The `hr_db` database is created automatically by Docker Compose using the `MYSQL_DATABASE` setting.

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

#### 4. Generate the employee master

The daily DAG expects `/opt/airflow/data/employee_master.csv`. Generate the initial 500-record file once:

```powershell
docker compose exec airflow-scheduler python /opt/airflow/scripts/create_employee_master.py
```

After this one-time setup, use the normal workflow above to start the services and trigger the pipelines from the Airflow UI.

### Official Airflow Compose download

The [official Airflow Docker quick start](https://airflow.apache.org/docs/apache-airflow/2.8.1/howto/docker-compose/index.html) uses the following command to download its standard Compose file:

```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.8.1/docker-compose.yaml'
```

On Windows PowerShell, use `curl.exe` if `curl` is mapped to `Invoke-WebRequest`. This repository already includes a customized `airflow-docker/docker-compose.yaml` with Kafka and MySQL, so do not run the download command inside this project unless you intend to replace that file. Docker downloads the Airflow image when the Compose stack is built or started.

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

Run these commands from the `airflow-docker` directory.

View service status:

```powershell
docker compose ps
```

Follow Airflow scheduler logs:

```powershell
docker compose logs -f airflow-scheduler
```

Follow Kafka or MySQL logs:

```powershell
docker compose logs -f kafka
docker compose logs -f mysql
```

Open a MySQL shell:

```powershell
docker compose exec mysql mysql -uroot -p hr_db
```

Stop the stack without deleting persisted data:

```powershell
docker compose down
```


