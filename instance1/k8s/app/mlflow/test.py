import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# MLflow Tracking URI 설정
mlflow.set_tracking_uri("/app/mlruns")  # Pod 내의 mlruns 경로로 설정

# 데이터 준비
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.2, random_state=42)

# 모델 훈련
model = RandomForestClassifier()
model.fit(X_train, y_train)

# MLflow에 모델 등록
with mlflow.start_run():
    mlflow.sklearn.log_model(model, "random_forest_model")
    mlflow.log_param("n_estimators", model.n_estimators)
    mlflow.log_param("max_depth", model.max_depth)

print("모델이 등록되었습니다.")
