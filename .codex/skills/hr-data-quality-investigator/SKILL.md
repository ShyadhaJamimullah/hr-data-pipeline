---
name: hr-data-quality-investigator
description: Investigate HR analytics pipeline issues using project files, Docker Compose, Airflow DAGs, Kafka scripts, SQL transformations, and MySQL tables.
---

# HR Data Quality Investigator

Use this skill when I ask to inspect, debug, validate, or understand my HR analytics pipeline.

## Available tools

Use filesystem MCP to inspect:
- docker-compose.yaml
- dags/
- scripts/
- sql/
- requirements.txt
- .env.example
- project structure

Use MySQL MCP to inspect:
- database schema
- table names
- row counts
- sample rows
- raw, staging, fact, and dimension tables

## My project flow

The HR analytics pipeline works like this:

1. Docker Compose starts services.
2. Airflow orchestrates the pipeline.
3. Python scripts generate HR snapshot data.
4. Kafka producer sends employee snapshot rows as events.
5. Kafka consumer loads events into MySQL raw table.
6. SQL transformations move data from raw to staging, fact, and dimension tables.
7. MySQL stores the final analytical tables.

## Main purpose

This skill is for investigation, validation, and learning.

It should help answer:
- Are raw and staging row counts matching?
- Are there duplicate employee records?
- Are SnapshotDate values correct?
- Are important HR columns null?
- Did Kafka-loaded data reach the raw table?
- Did SQL transformations produce expected outputs?
- Which layer may have caused a problem?

## Important boundary

Do not automatically:
- start Docker
- stop Docker
- trigger Airflow DAGs
- delete data
- update data
- insert data
- drop tables
- rewrite project files

unless I clearly ask.

## Investigation workflow

When investigating:

1. First inspect project files if table or flow names are unclear.
2. Identify the suspected layer:
   - Docker
   - Airflow DAG
   - Kafka producer
   - Kafka consumer
   - raw MySQL table
   - staging table
   - fact table
   - dimension table

3. Use MySQL MCP only for read-only checks.

4. Start with:
   - SHOW TABLES
   - DESCRIBE table_name
   - SELECT COUNT(*)
   - GROUP BY checks
   - LIMIT sample rows

5. Check for:
   - duplicate EmployeeID values
   - duplicate EmployeeID + SnapshotDate records
   - null SnapshotDate
   - missing Department
   - invalid MonthlyIncome
   - unexpected Relieved values
   - raw vs staging count mismatch
   - staging vs fact table mismatch

6. Explain findings in simple language.

7. Suggest fixes only after identifying the likely cause.

## SQL safety rules

Do not run these unless I explicitly ask:
- DELETE
- UPDATE
- DROP
- TRUNCATE
- ALTER
- INSERT
- CREATE

Prefer:
- SELECT
- SHOW
- DESCRIBE
- COUNT
- GROUP BY
- HAVING
- LIMIT

## Secret safety

Do not print or expose:
- passwords
- API keys
- tokens
- connection strings
- secret values from .env files

If .env files are inspected, explain only what the variables are for, not their values.

## Example checks

Check available tables:

```sql
SHOW TABLES;