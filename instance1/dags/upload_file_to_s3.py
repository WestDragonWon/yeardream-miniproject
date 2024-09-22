import os
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.models import Variable
from datetime import datetime

DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
}
#경로설정 
DIR_PATH=os.path.abspath(__file__)
SCRIPT_PATH = f"{DIR_PATH}/script"
DATA_PATH = Variable.get("DATA_PATH")
S3_PATH = Variable.get("S3_PATH")
TOPIC_NAME = Variable.get("TOPIC_NAME")

with DAG(
    'upload_file_to_s3',
    default_args=DEFAULT_ARGS,
    schedule_interval=None,
) as dag:
    upload_task = BashOperator(
        task_id='upload_to_s3',
        bash_command=f'python3 {SCRIPT_PATH}/push2s3.py {DATA_PATH} {S3_PATH}',
    )

    producer_task = BashOperator(
            task_id='producer_to_kafka',
            bash_command=f'python3 {SCRIPT_PATH}/kafka-producer.py {DATA_PATH} {TOPIC_NAME}',
    )
    
    producer_task

