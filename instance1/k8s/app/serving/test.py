import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# MLflow 서버 URL 설정
mlflow.set_tracking_uri("http://10.103.73.87:8080")
mlflow.set_experiment("testjun")

# 데이터셋 로드
iris = datasets.load_iris()
X = iris.data
y = iris.target

# 훈련 데이터와 테스트 데이터로 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# MLflow 설정
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
