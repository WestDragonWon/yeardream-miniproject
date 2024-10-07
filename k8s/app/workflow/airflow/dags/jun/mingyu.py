from datetime import datetime
import os
import pandas as pd
import boto3
from sqlalchemy import create_engine
from io import StringIO
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from mlflow.tracking import MlflowClient
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

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


# PostgreSQL 접속 정보
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_host = os.getenv("POSTGRES_HOST")
db_port = os.getenv("POSTGRES_PORT")
db_name = os.getenv("POSTGRES_DB")
table = os.getenv("POSTGRES_TABLE")

# PostgreSQL에서 데이터 로드
def load_data_from_postgres():
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    df = pd.read_sql_table(table, engine)
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

# Airflow DAG 정의
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 10, 7),
    'retries': 1,
}

dag = DAG(
    'iris_model_training_mingyu',
    default_args=default_args,
    description='A simple DAG for training an iris classification model',
    schedule_interval='@once',
)

train_model_task = PythonOperator(
    task_id='train_and_log_model',
    python_callable=train_and_log_model,
    dag=dag,
)

# 작업 의존성 설정
train_model_task