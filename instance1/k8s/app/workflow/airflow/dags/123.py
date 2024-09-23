from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

def print_hello():
    print("Hello, World!")

default_args = {
    'start_date': datetime(2023, 9, 22),
}

with DAG('simple_hello_world3',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:

    hello_task = PythonOperator(
        task_id='hello_task',
        python_callable=print_hello
    ) 

123