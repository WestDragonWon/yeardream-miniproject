from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import boto3
import os

# CSV file
CSV_FILE_PATH = '/opt/airflow/dags/data/iris_dataset20.csv'

# S3 설정
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_REGION = 'ap-northeast-2'
BUCKET_NAME = 'team06-rawdata'
S3_KEY = '/csv-iris/iris_dataset20.csv'

def upload_csv_to_s3():
    # boto3 클라이언트 생성
    s3_client = boto3.client(
        's3',
        region_name=S3_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    
    # binary모드로 읽기, upload_fileobj()매서드가 작은 청크사이즈로 잘라 청크를 읽고 쓰기 때문에 메모리 부족을 방지할 수 있음
    with open(CSV_FILE_PATH, 'rb') as f:
        s3_client.upload_fileobj(f, BUCKET_NAME, S3_KEY)
    
    print(f"File {CSV_FILE_PATH} uploaded to s3://{BUCKET_NAME}/{S3_KEY}")

with DAG(
    'upload_csv_to_s3_dag',
    default_args={
        'owner': 'airflow',
        'start_date': days_ago(1),
        'retries': 1,
    },
    description='Upload CSV to S3 via Airflow DAG',
    schedule_interval=None,  
) as dag:

    # CSV to S3
    upload_csv_task = PythonOperator(
        task_id='upload_csv_to_s3',
        python_callable=upload_csv_to_s3,
    )

    upload_csv_task





