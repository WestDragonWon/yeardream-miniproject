from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from confluent_kafka import Producer
import pandas as pd
import csv
import io


# Kafka 설정
KAFKA_TOPIC = 'large-csv-topic'
KAFKA_BOOTSTRAP_SERVERS = 'kafka-1:9092,kafka-2:9092,kafka-3:9092'

# CSV file경로(조정필요)
CSV_FILE_PATH = '/opt/airflow/dags/data/iris_dataset20.csv'


# Chunk size 5000 (100이상 오퍼레이터)느림 50000 (20미만 오퍼레이터) 500000 (2개) 제일빠름 operator 개수도 속도에 큰 영향을 줌
CHUNK_SIZE = 500000

def send_chunk_to_kafka(chunk_number, **kwargs):
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'batch.size': 131072,  # 128 KB batches
        'linger.ms': 50,  # Slight delay to batch more messages
        'message.max.bytes': 4194304,  # 4 MB message size limit
        'compression.type': 'gzip',  # Use compression to reduce payload size
        'acks': 'all',  # Ensure durability by waiting for all replicas
    }
    producer = Producer(conf)

    start_row = chunk_number * CHUNK_SIZE
    end_row = (chunk_number + 1) * CHUNK_SIZE

    try:
        chunk = pd.read_csv(CSV_FILE_PATH, skiprows=range(1, start_row + 1), nrows=CHUNK_SIZE, header=0)
        
        # Convert chunk to CSV string
        csv_buffer = io.StringIO()
        chunk.to_csv(csv_buffer, index=False)
        csv_string = csv_buffer.getvalue()

        # Send the entire chunk as one message
        producer.produce(KAFKA_TOPIC, key=str(chunk_number), value=csv_string.encode('utf-8'))
        producer.flush()
        
        return f"Chunk {chunk_number} sent successfully"
    except Exception as e:
        return f"Error processing chunk {chunk_number}: {str(e)}"

def count_chunks():
    total_rows = sum(1 for _ in open(CSV_FILE_PATH)) - 1  # Subtract 1 for header
    return (total_rows // CHUNK_SIZE) + (1 if total_rows % CHUNK_SIZE else 0)

with DAG(
    'send_csv_chunk_to_kafka',
    default_args={'owner': 'airflow'},
    description='Send CSV file to Kafka in chunks',
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['kafka', 'csv'],
) as dag:

    # Count total chunks at DAG definition time
    total_chunks = count_chunks()

    for i in range(total_chunks):
        PythonOperator(
            task_id=f'send_chunk_{i}',
            python_callable=send_chunk_to_kafka,
            op_kwargs={'chunk_number': i},
        )