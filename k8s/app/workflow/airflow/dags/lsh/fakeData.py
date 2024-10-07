from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from confluent_kafka import Producer
import json

# Kafka configuration
KAFKA_TOPIC = 'iris-topic1'
KAFKA_BOOTSTRAP_SERVERS = 'kafka-1:9092,kafka-2:9092,kafka-3:9092'

# Your JSON data
IRIS_DATA = [
    {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
        "species": "setosa"
    },
    {
        "sepal_length": 15.0,
        "sepal_width": 5.0,
        "petal_length": 20.0,
        "petal_width": 7.5,
        "species": "versicolor"
    },
    {
        "sepal_length": 29.7,
        "sepal_width": 9.9,
        "petal_length": 39.9,
        "petal_width": 14.9,
        "species": "virginica"
    }
]

def send_fakedata_to_kafka(**context):
    producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})
    
    try:
        # Send each record in the IRIS_DATA
        for record in IRIS_DATA:
            producer.produce(
                KAFKA_TOPIC,
                value=json.dumps(record).encode('utf-8')
            )
            producer.flush()
        
        print(f"Successfully sent {len(IRIS_DATA)} records to Kafka")
        return "Data sent successfully"
    
    except Exception as e:
        print(f"Error sending data to Kafka: {str(e)}")
        raise e
    
    finally:
        producer.flush()

# Define the DAG
with DAG(
    'send_iris_data_to_kafka',
    default_args={
        'owner': 'airflow',
        'retries': 1,
    },
    description='Send Iris JSON data to Kafka every minute',
    schedule_interval='* * * * *',  # Run every minute
    start_date=days_ago(1),
    catchup=False,
    tags=['iris', 'kafka'],
) as dag:

    send_data_task = PythonOperator(
        task_id='send_iris_data',
        python_callable=send_fakedata_to_kafka,
    )

    # Set task dependencies
    send_data_task