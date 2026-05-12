import json
import sys
import os

import logging
from kafka import KafkaConsumer
import mysql.connector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


KAFKA_TOPIC = "hr_daily_snapshot_events"
KAFKA_BOOTSTRAP_SERVER = "kafka:29092"


def consume_snapshot_events(snapshot_date):
    mysql_password = os.getenv("MYSQL_ROOT_PASSWORD")
    mysql_database = os.getenv("MYSQL_DATABASE")

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id=f"hr_daily_snapshot_consumer_{snapshot_date}",
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        consumer_timeout_ms=15000
    )

    conn = mysql.connector.connect(
        host="mysql",
        port=3306,
        user="root",
        password=mysql_password,
        database=mysql_database
    )

    cursor = conn.cursor()

    delete_query = """
    DELETE FROM hr_transactions_raw
    WHERE SnapshotDate = %s
    """

    insert_query = """
    INSERT INTO hr_transactions_raw (
        EmployeeID,
        EmployeeName,
        Gender,
        DOB,
        Department,
        JobRole,
        HireDate,
        MonthlyIncome,
        Overtime,
        JobSatisfaction,
        PerformanceRating,
        Relieved,
        SnapshotDate
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(delete_query, (snapshot_date,))

    inserted_count =0

    for message in consumer:
        event = message.value

        if str(event.get("SnapshotDate")) != snapshot_date:
            continue

        cursor.execute(insert_query, (
            event["EmployeeID"],
            event["EmployeeName"],
            event["Gender"],
            event["DOB"],
            event["Department"],
            event["JobRole"],
            event["HireDate"],
            event["MonthlyIncome"],
            event["Overtime"],
            event["JobSatisfaction"],
            event["PerformanceRating"],
            event["Relieved"],
            event["SnapshotDate"]
        ))

        inserted_count += 1

    conn.commit()

    cursor.close()
    conn.close()
    consumer.close()

    logging.info(
    f"Inserted {inserted_count} records into hr_transactions_raw for {snapshot_date}"
)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("Snapshot date argument is required. Example: 2026-03-01")

    snapshot_date = sys.argv[1]
    consume_snapshot_events(snapshot_date)