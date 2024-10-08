import io
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine
import pyarrow.parquet as pq
import pandas as pd
import boto3
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from mlflow.tracking import MlflowClient
from datetime import datetime, timedelta



# Model versioning function
def generate_model_version():
    head_version = 1  # 수동으로 수정 가능
    current_date = datetime.now()
    yearweek = current_date.strftime("%y%U")
    build_file = "/tmp/.build_version.txt"
    
    if os.path.exists(build_file):
        with open(build_file, "r") as f:
            last_version = f.read().strip()
            last_build_version = int(last_version.split(".b")[1])
            build_version = last_build_version + 1
    else:
        build_version = 1

    version = f"{head_version}.{yearweek}.b{build_version}"

    with open(build_file, "w") as f:
        f.write(str(version))

    return version

# S3, PostgreSQL 설정
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_REGION = 'ap-northeast-2'
bucket_name = 'team06-rawdata'

# PostgreSQL 접속 정보
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_host = os.getenv("POSTGRES_HOST")
db_port = os.getenv("POSTGRES_PORT")
db_name = os.getenv("POSTGRES_DB")
table = os.getenv("POSTGRES_TABLE")



def read_s3_and_store_to_postgres(**kwargs):
    # airflow가 스케줄로 4시에 돌면 logical_date는 3시
    previous_hour = kwargs['logical_date']
    
    # s3 폴더 경로 만들기
    s3_folder_path = f'iris-data/year={previous_hour.year}/month={previous_hour.month:02d}/day={previous_hour.day:02d}/hour={previous_hour.hour:02d}/'
    
    print(f"Checking S3 path: {s3_folder_path}")

    # AWS S3 연결
    s3 = boto3.client('s3', 
                      region_name=S3_REGION,
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    
    # Prefix 경로 안 파일 리스트를 response로 받음
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_folder_path)
    
    if 'Contents' not in response:
        print(f"No files found in {s3_folder_path}")
        return
    
    # SQLAlchemy engine
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    
    # 파일 리스트 안의 .parquet 파일들 읽기
    for obj in response['Contents']:
        s3_key = obj['Key']
        if s3_key.endswith('.parquet'):
            parquet_obj = s3.get_object(Bucket=bucket_name, Key=s3_key)
            body = parquet_obj['Body'].read()
            
            # pyarrow 라이브러리로 parquet형식 pandas DataFrame으로 변환
            data = pq.read_table(io.BytesIO(body)).to_pandas()
            
            # SQLAlchemy engine을 이용해 pandas DataFrame을 postgresql에 저장
            data.to_sql('iris_data_json', engine, if_exists='append', index=False)
            print(f"Data from {s3_key} has been appended to PostgreSQL.")

# PostgreSQL에서 데이터 로드
def load_data_from_postgres():
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    df = pd.read_sql_table(table, engine)
    #빈값 처리
    df = df.dropna()
    return df

# MLflow 모델 학습 및 로깅
def train_and_log_model():
    df = load_data_from_postgres()
    X = df.drop("species", axis=1).drop("idx", axis=1).drop("created_at", axis=1).values  # target_column을 예측 대상 열로 변경
    y = df["species"].values  # Species를 레이블로 설정

    # 데이터 전처리
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 학습 데이터와 테스트 데이터로 분리
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=123)

    # MLflow 설정
    mlflow.set_tracking_uri("http://mlflow:8080")  # MLflow 서버 URI
    mlflow.set_experiment("iris_classification_experiments_mingyu")

    # 모델 학습
    model = LogisticRegression(max_iter=200, C=0.5, solver='lbfgs', random_state=123)
    model.fit(X_train, y_train)
    
    # 예측 및 정확도 평가
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    accuracy = float(f"{accuracy:0.5f}")
    # MLflow에 모델 로그
    version = generate_model_version()
    client = MlflowClient()

    with mlflow.start_run(run_name=f"model_v{version}", nested=True) as run:
        run_id = run.info.run_id
        model_name = 'iris_model_mingyu'

        # 모델을 MLflow에 로그
        mlflow.sklearn.log_model(model, "model")
        mlflow.log_param("iris_param", model.get_params())
        mlflow.log_metric("iris_accuracy", accuracy)

        # 모델 등록 및 버전 관리
        try:
            model_versions = client.search_model_versions(f"name='{model_name}'")
            past_accuracy = float(client.get_registered_model(model_name).description) if model_versions else 0.0
            
            if accuracy >= 0.5:
                model_uri = f"runs:/{run_id}/model"
                registered_model = mlflow.register_model(model_uri=model_uri, name=model_name, tags={'accuracy': f"{accuracy:0.5f}"})
                
                if past_accuracy <= accuracy:
                    client.transition_model_version_stage(name=model_name, version=registered_model.version, stage="production")
                    client.update_registered_model(name=registered_model.name, description=f"{accuracy:0.5f}")
                    for i in range(1, int(registered_model.version)):
                        client.transition_model_version_stage(name=model_name, version=i, stage="archived")
                else:
                    client.transition_model_version_stage(name=model_name, version=registered_model.version, stage="archived")
                print(f"Model {model_name} version {registered_model.version} promoted to production.")
        except Exception as e:
            print(f"Error occurred: {e}")




default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 9, 26),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'iris_s3_pg_hourly_final',
    default_args=default_args,
    description='Hourly DAG to load iris data from S3 to PostgreSQL',
    schedule_interval='@hourly',
    catchup=False
)

task_read_s3_and_store_to_postgres = PythonOperator(
    task_id='read_s3_and_store_to_postgres',
    python_callable=read_s3_and_store_to_postgres,
    provide_context=True,
    dag=dag,
)

train_model_task = PythonOperator(
    task_id='train_and_log_model',
    python_callable=train_and_log_model,
    dag=dag,
)

task_read_s3_and_store_to_postgres >> train_model_task
