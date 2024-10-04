from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import pandas as pd
import boto3
from sqlalchemy import create_engine
import os
import io
import pyarrow.parquet as pq

# S3 and PostgreSQL configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_REGION = 'ap-northeast-2'
bucket_name = 'team06-rawdata'
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_host = 'postgres'
db_port = '5432'
db_name = 's32db'

def read_s3_and_store_to_postgres(**kwargs):
    # Get the execution date from Airflow context
    execution_date = kwargs['execution_date']
    
    # Calculate the start of the previous hour
    previous_hour = execution_date - timedelta(hours=1)
    
    # Construct S3 folder path for the previous hour
    s3_folder_path = f'iris-data/year={previous_hour.year}/month={previous_hour.month:02d}/day={previous_hour.day:02d}/hour={previous_hour.hour:02d}/'
    
    print(f"Checking S3 path: {s3_folder_path}")

    # AWS S3 client
    s3 = boto3.client('s3', 
                      region_name=S3_REGION,
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    
    # Get a list of files from S3
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_folder_path)
    
    if 'Contents' not in response:
        print(f"No files found in {s3_folder_path}")
        return
    
    # SQLAlchemy engine for PostgreSQL
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    
    # Loop through the files in the folder
    for obj in response['Contents']:
        s3_key = obj['Key']
        if s3_key.endswith('.parquet'):
            parquet_obj = s3.get_object(Bucket=bucket_name, Key=s3_key)
            body = parquet_obj['Body'].read()
            
            # Convert to pandas DataFrame
            data = pq.read_table(io.BytesIO(body)).to_pandas()
            
            # Store the DataFrame to PostgreSQL, append to table
            data.to_sql('iris_data', engine, if_exists='append', index=False)
            print(f"Data from {s3_key} has been appended to PostgreSQL.")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 9, 26),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'iris_s3_pg_hourly',
    default_args=default_args,
    description='Hourly DAG to load iris data from S3 to PostgreSQL',
    schedule_interval='@hourly',
    catchup=False
)

task_read_s3_and_store_to_postgres = PythonOperator(
    task_id='read_s3_and_store_to_postgres',
    python_callable=read_s3_and_store_to_postgres,
    op_kwargs={'execution_date': '{{ execution_date }}'},
    dag=dag,
)s