from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import pandas as pd
import boto3
from rediscluster import RedisCluster
import json
from io import StringIO
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import os

# S3 버킷 및 파일 정보
bucket_name = 'team06-mlflow-feature'
s3_object_name = 'iris.csv'

# AWS 자격 증명 정보
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_REGION = 'ap-northeast-2'  # S3 버킷이 위치한 지역

# Redis 접속 정보
redis_host = 'redis-cluster'  # Redis 호스트
redis_port = '6379'            # Redis 포트

# Redis 클라이언트 연결을 전역 변수로 설정
redis_client = None

def get_redis_client():
    global redis_client
    if redis_client is None:
        startup_nodes = [{"host": redis_host, "port": redis_port}]
        redis_client = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)
    return redis_client

# S3에서 CSV 파일 읽기 및 Redis에 저장
def read_s3_and_store_to_redis():
    try:
        redis_client = get_redis_client()

        # AWS 자격 증명으로 S3 클라이언트 생성
        s3 = boto3.client('s3', 
                          region_name=S3_REGION,
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

        # S3에서 CSV 객체 가져오기
        csv_obj = s3.get_object(Bucket=bucket_name, Key=s3_object_name)
        body = csv_obj['Body'].read().decode('utf-8')
        data = pd.read_csv(StringIO(body))

        # Redis에 데이터를 배치로 저장
        pipeline = redis_client.pipeline()
        for index, row in data.iterrows():
            pipeline.set(f"row:{index}", json.dumps(row.to_dict()))
        pipeline.execute()  # 모든 명령을 한 번에 실행

        print("Data has been imported to Redis.")
    except Exception as e:
        print(f"Error reading from S3 or storing to Redis: {e}")
        raise  # 예외 발생 시 작업 실패로 처리

# Redis에서 데이터 불러오기 및 MLflow에 모델 저장
def load_from_redis_and_train_model():
    redis_client = get_redis_client()

    data = []
    index = 0

    try:
        while True:
            row = redis_client.get(f"row:{index}")
            if row is None:
                break
            data.append(json.loads(row))
            index += 1

        iris_data = pd.DataFrame(data)

        # MLflow 설정
        mlflow.set_tracking_uri("http://mlflow:8080")
        mlflow.set_experiment("iris_experiment")

        # MLflow 실행 시작
        mlflow.start_run()

        # 특징(X)과 레이블(y) 분리
        X = iris_data.drop(columns='Species')
        y = iris_data['Species']

        # 훈련 데이터와 테스트 데이터로 분리
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 모델 훈련
        model = RandomForestClassifier(n_estimators=100)
        model.fit(X_train, y_train)

        # 모델 저장
        model_path = "iris_model"
        mlflow.sklearn.log_model(model, model_path)

        # 모델 레지스트리에 등록
        model_uri = f"runs:/{mlflow.active_run().info.run_id}/{model_path}"
        mlflow.register_model(model_uri, "IrisModel")

        # MLflow 실행 종료
        mlflow.end_run()

        print("Model has been trained and logged to MLflow.")
    except Exception as e:
        print(f"Error loading data from Redis or training model: {e}")
        raise  # 예외 발생 시 작업 실패로 처리

# DAG 정의
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 9, 26),
    'retries': 1,
}

dag = DAG('redis', default_args=default_args, schedule_interval='@daily')

task_read_s3_and_store_to_redis = PythonOperator(
    task_id='read_s3_and_store_to_redis',
    python_callable=read_s3_and_store_to_redis,
    dag=dag,
)

task_load_from_redis_and_train_model = PythonOperator(
    task_id='load_from_redis_and_train_model',
    python_callable=load_from_redis_and_train_model,
    dag=dag,
)

task_read_s3_and_store_to_redis >> task_load_from_redis_and_train_model