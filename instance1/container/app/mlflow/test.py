import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


mlflow.set_tracking_uri("http://localhost:8080")
# 데이터 로드
data = load_iris()
X = data.data
y = data.target

# 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# MLflow 실험 설정
mlflow.set_experiment("Iris_Experiment")

# 모델 훈련 및 MLflow 기록
with mlflow.start_run():
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 예측 및 정확도 평가
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    
    # 메트릭 기록
    mlflow.log_metric("accuracy", accuracy)
    
    # 모델 저장
    mlflow.sklearn.log_model(model, "model")

    print(f"Logged model with accuracy: {accuracy}")