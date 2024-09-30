from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from confluent_kafka import Producer
import pandas as pd
import json
import os

# Kafka 설정
KAFKA_TOPIC = 'large-csv-topic'
KAFKA_BOOTSTRAP_SERVERS = ['kafka-1:9092'] 

# CSV file
CSV_FILE_PATH = './iris_dataset20.csv'

CHUNK_SIZE = 1024*1024 

def send_chunk_to_kafka(chunk_number, **kwargs):
    producer = Producer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        max_request_size=10485760  # 10MB, adjust as needed
    )

    start_row = chunk_number * CHUNK_SIZE
    end_row = (chunk_number + 1) * CHUNK_SIZE

    try:
        chunk = pd.read_csv(CSV_FILE_PATH, skiprows=range(1, start_row + 1), nrows=CHUNK_SIZE, header=0)
        
        # CSV to JSON
        for _, row in chunk.iterrows():
            producer.send(KAFKA_TOPIC, value=row.to_dict())
        
        producer.flush()
        return f"Chunk {chunk_number} sent successfully"
    except Exception as e:
        return f"Error processing chunk {chunk_number}: {str(e)}"
    finally:
        producer.close()

def count_chunks():
    total_rows = sum(1 for _ in open(CSV_FILE_PATH)) - 1 
    return (total_rows // CHUNK_SIZE) + (1 if total_rows % CHUNK_SIZE else 0)

with DAG(
    'send_json_chunk_to_kafka',
    default_args={'owner': 'airflow'},
    description='Send a json file to Kafka in chunks',
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['kafka', 'json'],
) as dag:
    # 청크 개수 확인
    count_chunks_task = PythonOperator(
        task_id='count_chunks',
        python_callable=count_chunks,
    )
    # 청크 순으로 청크를 인자로 받는 pythonOperator 생성
    def create_send_chunk_task(chunk_number):
        return PythonOperator(
            task_id=f'send_chunk_{chunk_number}',
            python_callable=send_chunk_to_kafka,
            op_kwargs={'chunk_number': chunk_number},
        )
    # task들을 list로 받아 각각의 청크가 send_chunk_to_kafka(청크넘버)를 실행하도록 함
    send_chunk_tasks = []
    for i in range(count_chunks_task.output):
        send_chunk_tasks.append(create_send_chunk_task(i))

    count_chunks_task >> send_chunk_tasks