from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from confluent_kafka import Producer
import pandas as pd
import csv
import io
import os

# Kafka 설정
KAFKA_TOPIC = 'iris-topic'
KAFKA_BOOTSTRAP_SERVERS = 'kafka-1:9092,kafka-2:9092,kafka-3:9092'

# CSV file경로
CSV_FILE_PATH = '/opt/airflow/dags/data/iris_dataset20.csv'

def send_csv_to_kafka():
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'batch.size': 131072,  # 128 KB 배치사이즈
        'linger.ms': 50,  # 많은 메시지 배치를 위한 딜레이
        'message.max.bytes': 4194304,  # 4 MB 메시지 최대 사이즈
        'compression.type': 'gzip',  # 압축
        'acks': 'all',  # Ensure durability by waiting for all replicas
    }
    producer = Producer(conf)
    
    try:
        # CSV file 확인
        if not os.path.exists(CSV_FILE_PATH):
            raise FileNotFoundError(f"{CSV_FILE_PATH} does not exist.")
        
        # pandas로 csv 파일 읽기
        df = pd.read_csv(CSV_FILE_PATH, header=0)
        
        # index를 포함한 csv 형태로 만들기
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=True)
        csv_string = csv_buffer.getvalue()
        
        # pandas로 읽고 변환한 csv 사이즈
        csv_size = len(csv_string.encode('utf-8'))
        print(f"CSV size: {csv_size} bytes")
        
        # csv사이즈와 카프카 메시지 최대 사이즈 비교
        if csv_size > conf['message.max.bytes']:
            raise ValueError(f"CSV size exceeds the Kafka message size limit of {conf['message.max.bytes']} bytes")
        
        # kafka로 내보내기
        producer.produce(KAFKA_TOPIC, key="1", value=csv_string.encode('utf-8'))
        producer.flush()
        
        print("CSV sent to Kafka successfully")
    except Exception as e:
        print(f"Error sending CSV to Kafka: {str(e)}")
        raise

with DAG(
    'send_csv_to_kafka',
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