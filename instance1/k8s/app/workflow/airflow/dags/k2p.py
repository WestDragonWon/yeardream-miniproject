from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from confluent_kafka import Consumer, KafkaException
import psycopg2

KAFKA_BROKER = 'kafka-1:9092'
KAFKA_TOPIC = 'conn'

def consume_messages():
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BROKER,
        'auto.offset.reset': 'earliest'  # 그룹 ID 없이 사용
    })
    
    consumer.subscribe([KAFKA_TOPIC])
    
    messages = []
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                break
            if msg.error():
                raise KafkaException(msg.error())
            messages.append(msg.value().decode('utf-8'))
    except Exception as e:
        print(f"Error while consuming messages: {e}")
    finally:
        consumer.close()
    
    return messages

def insert_into_postgres(messages):
    conn = psycopg2.connect(
        dbname='your_db_name',  # PostgreSQL 데이터베이스 이름
        user='your_user',       # PostgreSQL 사용자
        password='your_password', # PostgreSQL 비밀번호
        host='postgres',        # PostgreSQL 서비스 이름
        port='5432'             # PostgreSQL 포트
    )
    cursor = conn.cursor()
    
    for message in messages:
        # 메시지를 PostgreSQL에 삽입하는 SQL 쿼리
        cursor.execute("INSERT INTO your_table_name (column_name) VALUES (%s)", (message,))
    
    conn.commit()
    cursor.close()
    conn.close()

with DAG(
    dag_id='kafka_to_postgres',
    schedule_interval='@once',
    start_date=datetime(2024, 9, 23),
    catchup=False,
) as dag:
    
    consume_kafka = PythonOperator(
        task_id='consume_kafka',
        python_callable=consume_messages,
    )

    insert_postgres = PythonOperator(
        task_id='insert_postgres',
        python_callable=insert_into_postgres,
        op_kwargs={'messages': '{{ task_instance.xcom_pull(task_ids="consume_kafka") }}'},
    )

    consume_kafka >> insert_postgres
