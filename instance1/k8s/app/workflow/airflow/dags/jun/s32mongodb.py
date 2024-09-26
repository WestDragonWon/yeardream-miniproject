from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import os
import csv
import boto3
from pymongo import MongoClient

# S3와 MongoDB 환경변수에서 시크릿 값 가져오기
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = 'team06-mlflow-feature'
S3_REGION = 'ap-northeast-2'
S3_FILE_KEY = 'iris.csv'  # S3에 있는 CSV 파일의 경로

MONGO_URI = "mongodb://mongodb:27017"  # MongoDB 주소
MONGO_DB = "mongo"  # MongoDB 데이터베이스 이름
MONGO_COLLECTION = "test"  # MongoDB 컬렉션 이름

def fetch_csv_from_s3():
    # S3 클라이언트 설정
    s3 = boto3.client('s3', 
                      region_name=S3_REGION,
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    
    # S3에서 파일 다운로드
    obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_FILE_KEY)
    csv_data = obj['Body'].read().decode('utf-8').splitlines()
    return csv.reader(csv_data)

def insert_data_to_mongo(**kwargs):
    # MongoDB 클라이언트 설정
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    csv_data = fetch_csv_from_s3()

    # 데이터 삽입
    for row in csv_data:
        document = {"column1": row[0], "column2": row[1], "column3": row[2]}  # 컬럼에 맞게 수정
        collection.insert_one(document)
    print("Data inserted successfully into MongoDB")

# DAG 정의
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 9, 25),
    'retries': 1,
}

with DAG('s3_to_mongo', default_args=default_args, schedule_interval='@once') as dag:

    insert_task = PythonOperator(
        task_id='insert_data_to_mongo',
        python_callable=insert_data_to_mongo,
        provide_context=True
    )
