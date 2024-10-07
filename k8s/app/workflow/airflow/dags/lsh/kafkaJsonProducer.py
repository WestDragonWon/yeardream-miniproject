from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from confluent_kafka import Producer
import json
import os

# Kafka configuration
KAFKA_TOPIC = 'iris-topic1'
KAFKA_BOOTSTRAP_SERVERS = 'kafka-1:9092,kafka-2:9092,kafka-3:9092'

# JSON file
JSON_FILE_PATH = '/opt/airflow/dags/data/iris_data.json'
CHUNK_SIZE = 100  # json 청크사이즈, message사이즈 조절시 필요

def send_chunk_to_kafka(chunk_number, **kwargs):
    producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})

    start_row = chunk_number * CHUNK_SIZE
    end_row = (chunk_number + 1) * CHUNK_SIZE

    try:
        with open(JSON_FILE_PATH, 'r') as file:
            #json을 한번에 읽으므로 큰 json파일은 안됨, streaming 또는 api 호출을 통한 메모리 사이즈 이하의 json데이터
            #특정
            data = json.load(file)
            chunk = data[start_row:end_row]

        for record in chunk:
            producer.produce(KAFKA_TOPIC, value=json.dumps(record).encode('utf-8'))
        
        producer.flush()
        return f"Chunk {chunk_number} sent successfully"
    except Exception as e:
        return f"Error processing chunk {chunk_number}: {str(e)}"
    finally:
        producer.flush()

def count_chunks():
    with open(JSON_FILE_PATH, 'r') as file:
        data = json.load(file)
    total_records = len(data)
    return (total_records // CHUNK_SIZE) + (1 if total_records % CHUNK_SIZE else 0)

with DAG(
    'send_json_chunk_to_kafka',
    default_args={'owner': 'airflow'},
    description='Send a JSON file to Kafka in chunks',
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['kafka', 'json'],
) as dag:

    count_chunks_task = PythonOperator(
        task_id='count_chunks',
        python_callable=count_chunks,
    )

    def create_send_chunk_task(i):
        return PythonOperator(
            task_id=f'send_chunk_{i}',
            python_callable=send_chunk_to_kafka,
            op_kwargs={'chunk_number': i},
        )

    count_chunks_task >> [create_send_chunk_task(i) for i in range(count_chunks())]