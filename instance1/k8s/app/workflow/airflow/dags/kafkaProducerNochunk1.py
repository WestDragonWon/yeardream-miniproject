from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from confluent_kafka import Producer
import pandas as pd
import csv
import io
import os

# Kafka 설정
KAFKA_TOPIC = 'large-csv-topic-all'
KAFKA_BOOTSTRAP_SERVERS = 'kafka-1:9092,kafka-2:9092,kafka-3:9092'

# CSV file경로
CSV_FILE_PATH = '/opt/airflow/dags/data/iris_dataset20.csv'


def send_chunk_to_kafka():
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'batch.size': 131072,  # 128 KB batches
        'linger.ms': 50,  # Slight delay to batch more messages
        'message.max.bytes': 4194304,  # 4 MB message size limit
        'compression.type': 'gzip',  # Use compression to reduce payload size
        'acks': 'all',  # Ensure durability by waiting for all replicas
    }
    producer = Producer(conf)

    try:
        chunk = pd.read_csv(CSV_FILE_PATH, header=0)
        
        # Convert chunk to CSV string
        csv_buffer = io.StringIO()
        chunk.to_csv(csv_buffer, index=True)
        csv_string = csv_buffer.getvalue()

        # Send the entire chunk as one message
        producer.produce(KAFKA_TOPIC, key=str(1), value=csv_string.encode('utf-8'))
        producer.flush()
        
        return f"sent successfully"
    except Exception as e:
        return f"Error processing"

with DAG(
    'send_allcsv_to_kafka',
    default_args={'owner': 'airflow'},
    description='Send CSV file to Kafka in chunks',
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['kafka', 'csv'],
) as dag:
        PythonOperator(
            task_id=f'send_csv',
            python_callable=send_chunk_to_kafka,
        )