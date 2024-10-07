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
from version_control import generate_model_version
from mlflow.tracking import MlflowClient
import os

# S3 버킷 및 파일 정보
bucket_name = 'team06-mlflow-feature'  # S3 버킷 이름
s3_object_name = 'iris.csv'  # S3 객체 경로

# PostgreSQL 접속 정보
db_user = "mlops_user"  # PostgreSQL 사용자 이름
db_password = "1234"  # PostgreSQL 비밀번호
db_host = "localhost" 
db_port = "5432"  # PostgreSQL 포트
db_name = "s32db"  # 데이터베이스 이름
table = "iris_data"  # 테이블 이름

# S3에서 CSV 파일 읽기
def load_data_from_s3():
    s3 = boto3.client('s3')
    csv_obj = s3.get_object(Bucket=bucket_name, Key=s3_object_name)
    body = csv_obj['Body'].read().decode('utf-8')
    return pd.read_csv(StringIO(body))

# PostgreSQL에 데이터 로드
def load_data_to_postgres(df):
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    df.to_sql('iris_data', engine, if_exists='replace', index=False)  # 'iris_data'는 테이블 이름

# PostgreSQL에서 데이터 로드
def load_data_from_postgres():
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    df = pd.read_sql_table(table, engine)
    df = df.dropna()
    return df

# MLflow 모델 학습 및 로깅
def train_and_log_model(df):
    # 데이터프레임 구조 확인
    print("DataFrame columns:", df.columns)

    # Features와 Target 변수 설정
    X = df.drop("Species", axis=1)  # Species 열을 예측 대상 열로 변경
    y = df["Species"]  # Species를 레이블로 설정

    # 데이터 전처리
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 학습 데이터와 테스트 데이터로 분리
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=123)

    # MLflow 설정
    mlflow.set_tracking_uri("http://localhost:30003")  # MLflow 서버 URI
    mlflow.set_experiment("iris_classification_experiments")

    # 모델 학습
    model = LogisticRegression(max_iter=200, C=0.5, solver='lbfgs', random_state=123)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # MLflow에 모델 로그
    version = generate_model_version()
    client = MlflowClient()

    with mlflow.start_run(run_name=f"model_v{version}", nested=True) as run:
        run_id = run.info.run_id
        model_name = 'iris_model'

        # 모델을 MLflow에 로그
        mlflow.sklearn.log_model(model, "model")
        mlflow.log_param("iris_param", model.get_params())
        mlflow.log_metric("iris_accuracy", accuracy)

        # 모델 등록 및 버전 관리
        try:
            model_versions = client.search_model_versions(f"name='{model_name}'")
            past_accuracy = float(client.get_registered_model(model_name).description) if model_versions else 0.0

            if past_accuracy <= accuracy:
                model_uri = f"runs:/{run_id}/model"
                registered_model = mlflow.register_model(model_uri=model_uri, name=model_name, tags={'accuracy': f"{accuracy:0.5f}"})
                client.update_registered_model(name=registered_model.name, description=f"{accuracy:0.5f}")

                client.transition_model_version_stage(name=model_name, version=registered_model.version, stage="production")
                for i in range(1, int(registered_model.version)):
                    client.transition_model_version_stage(name=model_name, version=i, stage="archived")

                print(f"Model {model_name} version {registered_model.version} promoted to production.")
        except Exception as e:
            print(f"Error occurred: {e}")

# Main execution
if __name__ == "__main__":
    # S3에서 데이터 로드
    df = load_data_from_s3()
    # PostgreSQL에 데이터 로드
    load_data_to_postgres(df)
    # PostgreSQL에서 데이터 로드
    df = load_data_from_postgres()
    # 모델 학습 및 로깅
    train_and_log_model(df)
