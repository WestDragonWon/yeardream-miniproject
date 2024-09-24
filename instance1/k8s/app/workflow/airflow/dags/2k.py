from datetime import datetime
from airflow.decorators import dag
from airflow.operators.python import PythonOperator
import json
from confluent_kafka import Producer
import pendulum
import random

KAFKA_TOPIC = 'conn'
KAFKA_BROKER = 'kafka-1:9092'

def create_kafka_producer():
    return Producer({
        'bootstrap.servers': KAFKA_BROKER
    })

def generate_random_data(**context):
    all_data = []
    max_records = 10

    for _ in range(max_records):
        random_data = {
            'id': random.randint(1000, 9999),
            'name': f'User_{random.randint(1, 100)}',
            'score': random.randint(0, 100),
            'timestamp': datetime.now().isoformat()
        }
        all_data.append(random_data)

    context['task_instance'].xcom_push(key='random_data', value=json.dumps(all_data))

def send_data_to_kafka(**context):
    producer = create_kafka_producer()
    
    data = context['task_instance'].xcom_pull(task_ids='generate_random_data_task', key='random_data')
    
    if data is None:
        return

    records = json.loads(data)

    for record in records:
        key = str(record['id'])
        value = json.dumps(record)
        
        try:
            producer.produce(KAFKA_TOPIC, key=key, value=value)
        except Exception as e:
            print(f"Error producing message to Kafka: {e}")

    producer.flush()

local_tz = pendulum.timezone("Asia/Seoul")

@dag(
    start_date=datetime(2024, 9, 23, tzinfo=local_tz),
    schedule='@daily',
    catchup=False
)
def random_data_kafka_dag():
    generate_random_data_task = PythonOperator(
        task_id='generate_random_data_task',
        python_callable=generate_random_data,
        provide_context=True,
    )

    send_data_to_kafka_task = PythonOperator(
        task_id='send_data_to_kafka_task',
        python_callable=send_data_to_kafka,
        provide_context=True,
    )

    generate_random_data_task >> send_data_to_kafka_task

dag_instance = random_data_kafka_dag()
