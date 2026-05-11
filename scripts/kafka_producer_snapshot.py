import json
import sys
import time
import os
import pandas as pd
from kafka import KafkaProducer


KAFKA_TOPIC = "hr_daily_snapshot_events"
KAFKA_BOOTSTRAP_SERVER = "kafka:29092"


def send_snapshot_to_kafka(snapshot_date):
    file_name = f"snapshot_{snapshot_date.replace('-', '')}.csv"
    file_path = os.path.join("/opt/airflow/data", file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Snapshot file not found: {file_path}")

    df = pd.read_csv(file_path)

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
        value_serializer=lambda value: json.dumps(value, default=str).encode("utf-8"),
        key_serializer=lambda key: str(key).encode("utf-8")
    )

    sent_count = 0

    for _, row in df.iterrows():
        event = row.to_dict()
        event["event_type"] = "employee_daily_snapshot"

        producer.send(
            KAFKA_TOPIC,
            key=event["EmployeeID"],
            value=event
        )

        sent_count += 1
        print(f"Sent EmployeeID {event['EmployeeID']} to Kafka")
        time.sleep(0.01)

    producer.flush()
    producer.close()

    print(f"Sent {sent_count} records to Kafka topic: {KAFKA_TOPIC}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("Snapshot date argument is required. Example: 2026-03-01")

    snapshot_date = sys.argv[1]
    send_snapshot_to_kafka(snapshot_date)