from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from confluent_kafka import Producer
import pandas as pd
import csv
import io
import os

# Kafka configuration
KAFKA_TOPIC = 'large-csv-topic-all'
KAFKA_BOOTSTRAP_SERVERS = 'kafka-1:9092,kafka-2:9092,kafka-3:9092'

# CSV file path
CSV_FILE_PATH = '/opt/airflow/dags/data/iris_dataset20.csv'

def send_csv_to_kafka():
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
        # Check if the CSV file exists
        if not os.path.exists(CSV_FILE_PATH):
            raise FileNotFoundError(f"{CSV_FILE_PATH} does not exist.")
        
        # Read the entire CSV file into a pandas DataFrame
        df = pd.read_csv(CSV_FILE_PATH, header=0)
        
        # Convert the DataFrame to CSV string, including the index
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=True)
        csv_string = csv_buffer.getvalue()
        
        # Log the size of the CSV string
        csv_size = len(csv_string.encode('utf-8'))
        print(f"CSV size: {csv_size} bytes")
        
        # Ensure the total size of the data is below the Kafka message limit
        if csv_size > conf['message.max.bytes']:
            raise ValueError(f"CSV size exceeds the Kafka message size limit of {conf['message.max.bytes']} bytes")
        
        # Send the entire CSV as one message
        producer.produce(KAFKA_TOPIC, key="1", value=csv_string.encode('utf-8'))
        producer.flush()
        
        print("CSV sent to Kafka successfully")
    except Exception as e:
        print(f"Error sending CSV to Kafka: {str(e)}")
        raise

# DAG definition
with DAG(
    'send_allcsv_to_kafka',
    default_args={'owner': 'airflow'},
    description='Send CSV file to Kafka',
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['kafka', 'csv'],
) as dag:

    PythonOperator(
        task_id='send_csv',
        python_callable=send_csv_to_kafka,
    )

"""[2024-09-26, 00:16:42 UTC] {taskinstance.py:1206} INFO - Marking task as FAILED. dag_id=send_allcsv_to_kafka, task_id=send_csv, run_id=manual__2024-09-26T00:15:36.752119+00:00, execution_date=20240926T001536, start_date=20240926T001639, end_date=20240926T001642
[2024-09-26, 00:16:42 UTC] {standard_task_runner.py:110} ERROR - Failed to execute job 478 for task send_csv (CSV size exceeds the Kafka message size limit of 4194304 bytes; 130)

message.max.bytes를 늘려주거나 데이터를 잘라서 넣어줘야함
"""