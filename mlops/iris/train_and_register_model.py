import psycopg2
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from version_control import generate_model_version
from mlflow.tracking import MlflowClient
import os
from sqlalchemy import create_engine

host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
database = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
table = os.getenv("POSTGRES_TABLE")
pw = os.getenv("POSTGRES_PASSWORD")

# PostgreSQL 연결 및 데이터 불러오기
def load_data_from_postgres():
    # PostgreSQL 연결 설정
    try:
        #SQLAlchemy로 데이터베이스와 연결
        engine = create_engine(f'postgresql+psycopg2://{user}:{pw}@{host}:{port}/{database}')
        #conn = psycopg2.connect(
        #    host=host,
        #    database=database,
        #    user=user,
        #    password=pw
        #)
        print("connected")
    except Exception as e:
        print("connection fail")

    # SQL 쿼리를 통해 데이터를 읽어옴
    #query = f"SELECT * FROM {table};"  # 적절한 테이블 및 쿼리로 변경
    df = pd.read_sql_table(table, engine)
    df = df.dropna()
    #conn.close()
    return df

# Load dataset from PostgreSQL
df = load_data_from_postgres()
#X = df.drop("Species", axis=1).values  # target_column을 예측 대상 열로 변경
#y = df["Species"].values

X = df.drop("species", axis=1).drop("idx", axis=1).drop("created_at", axis=1).values  # target_column을 예측 대상 열로 변경
y = df["species"].values  # Species를 레이블로 설정

# Preprocess the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

#학습 데이터와 테스트 데이터로 분리
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=123)

# Set MLflow tracking URI
mlflow.set_tracking_uri("http://localhost:30003") #로컬에 설치된 쿠버네티스가 nodeport 형식으로 30003에 띄워져있어야 함
mlflow.set_experiment("iris_classification_experiments")

# Train the model and log it to MLflow
model = LogisticRegression(
    max_iter=200,
    C=0.5,
    solver='lbfgs',
    random_state=123
    )
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

# Generate version based on custom rules
version = generate_model_version()

# MLflow client for model registration
client = MlflowClient()

# Start MLflow run
with mlflow.start_run(run_name=f"model_v{version}", nested=True) as run:

    run_id = run.info.run_id # 현재의 run ID
    experiment_id = run.info.experiment_id # 현재의 experiment ID
    model_name = 'iris_model'

    # Log the model to MLflow
    mlflow.sklearn.log_model(model, "model") # 모델을 artifact 디렉토리에 저장

    mlflow.log_param("iris_param", model.get_params())
    mlflow.log_metric("iris_accuracy", accuracy)

    # get best accuracy :
    try:
        model_versions = client.search_model_versions(f"name='{model_name}'")
        if model_versions:
            registered_model = client.get_registered_model(model_name)
            past_accuracy = float(registered_model.description)
        else:
            past_accuracy = 0.0
    except Exception as e:
        print(f"error occured: {e}")

    if past_accuracy <= accuracy:
        # Register the model to MLflow Model Registry
        model_uri = f"runs:/{run_id}/model"
        registered_model = mlflow.register_model(model_uri=model_uri, name=model_name, tags = {'accuracy':f"{accuracy:0.5f}"})
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@', model_uri, '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        client.update_registered_model(name=registered_model.name, description=f"{accuracy:0.5f}")

        try:
            client.transition_model_version_stage(
                name=model_name,
                version=registered_model.version,
                stage="production"
            )
            print(f"Model {model_name} version {registered_model.version} promoted to production.")
        except Exception as e:
            print(f"Failed to promote model to production: {e}")
        
        for i in range(1, int(registered_model.version)):
            client.transition_model_version_stage(
                    name=model_name,
                    version=i,
                    stage="archived"
                    )
