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

# S3 버킷 및 파일 정보
bucket_name = 'team06-mlflow-feature'
s3_object_name = 'iris.csv'

# Redis 클러스터 접속 정보
startup_nodes = [{"host": "192.168.182.16", "port": "6379"}]
redis_client = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

# S3에서 CSV 파일 읽기 및 Redis에 저장
def read_s3_and_store_to_redis():
    s3 = boto3.client('s3')
    csv_obj = s3.get_object(Bucket=bucket_name, Key=s3_object_name)
    body = csv_obj['Body'].read().decode('utf-8')
    data = pd.read_csv(StringIO(body))

    for index, row in data.iterrows():
        redis_client.set(f"row:{index}", json.dumps(row.to_dict()))

    print("Data has been imported to Redis.")

# Redis에서 데이터 불러오기 및 MLflow에 모델 저장
def load_from_redis_and_train_model():
    data = []
    index = 0

    while True:
        row = redis_client.get(f"row:{index}")
        if row is None:
            break
        data.append(json.loads(row))
        index += 1

    iris_data = pd.DataFrame(data)

    # MLflow 설정
    mlflow.set_tracking_uri("http://10.103.73.87:8080")
    mlflow.set_experiment("iris_experiment")

    # MLflow 실행 시작
    with mlflow.start_run():
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

    print("Model has been trained and logged to MLflow.")

# DAG 정의
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 9, 26),
    'retries': 1,
}

# DAG 인스턴스 생성
with DAG(
    'redis_iris2321312',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False  # 실행되지 않은 DAG이 자동으로 catchup하지 않도록 설정
) as dag:

    # S3에서 데이터를 읽고 Redis에 저장하는 Task
    task_read_s3_and_store_to_redis = PythonOperator(
        task_id='read_s3_and_store_to_redis',
        python_callable=read_s3_and_store_to_redis
    )

    # Redis에서 데이터를 읽고 모델을 학습 및 MLflow에 저장하는 Task
    task_load_from_redis_and_train_model = PythonOperator(
        task_id='load_from_redis_and_train_model',
        python_callable=load_from_redis_and_train_model
    )

    # Task 종속성 설정
    task_read_s3_and_store_to_redis >> task_load_from_redis_and_train_model
