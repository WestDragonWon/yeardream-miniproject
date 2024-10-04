from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator  # Airflow 2.x에 맞게 수정
import pandas as pd
import boto3
from sqlalchemy import create_engine
from io import StringIO
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import os
import io 

# S3 버킷 및 파일 정보
bucket_name = 'team06-mlflow-feature'
s3_object_name = 'iris1.csv'

# AWS 자격 증명 정보
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_REGION = 'ap-northeast-2'                        # S3 버킷이 위치한 지역

# PostgreSQL 접속 정보
db_user = os.getenv("POSTGRES_USER")     # PostgreSQL 사용자 이름
db_password = os.getenv("POSTGRES_PASSWORD")   # PostgreSQL 비밀번호
db_host = 'postgres' 
db_port = '5432'                # PostgreSQL 포트
db_name = 's32db'               # 데이터베이스 이름

# S3에서 CSV 파일 읽기 및 PostgreSQL에 저장하는 함수
def read_s3_and_store_to_postgres():
    # AWS 자격 증명으로 S3 클라이언트 생성
    s3 = boto3.client('s3', 
                      region_name=S3_REGION,
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    # S3에서 CSV 객체 가져오기
    csv_obj = s3.get_object(Bucket=bucket_name, Key=s3_object_name)
    body = csv_obj['Body'].read().decode('utf-8')

    # 파일 내용을 pandas DataFrame으로 변환
    data = pd.read_csv(io.StringIO(body), sep=';')

    # SQLAlchemy를 사용하여 PostgreSQL 엔진 생성
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

    # 데이터프레임을 PostgreSQL에 로드
    data.to_sql('iris_data', engine, if_exists='replace', index=True)
    print("Data has been loaded into PostgreSQL.")

# PostgreSQL에서 데이터를 읽어와 모델을 훈련시키는 함수
def load_data_and_train_model():
    # SQLAlchemy를 사용하여 PostgreSQL 엔진 생성
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    
    # Iris 데이터 읽기
    iris_data = pd.read_sql('SELECT * FROM iris_data', engine)

    # 특징(X)과 레이블(y) 분리
    X = iris_data.drop(columns='Species')
    y = iris_data['Species']  

    # 훈련 데이터와 테스트 데이터로 분리
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # MLflow 설정
    mlflow.set_tracking_uri("http://mlflow:8080")  # MLflow 서버 URL
    mlflow.set_experiment("testjun")  # 실험 이름 설정

    # MLflow 실행 시작
    mlflow.start_run()

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

# DAG 정의
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 9, 26),
    'retries': 1,
}

dag = DAG('iris_model', default_args=default_args, schedule_interval='@daily')

task_read_s3_and_store_to_postgres = PythonOperator(
    task_id='read_s3_and_store_to_postgres',
    python_callable=read_s3_and_store_to_postgres,
    dag=dag,
)

task_load_data_and_train_model = PythonOperator(
    task_id='load_data_and_train_model',
    python_callable=load_data_and_train_model,
    dag=dag,
)

task_read_s3_and_store_to_postgres >> task_load_data_and_train_model

#수정 테스트