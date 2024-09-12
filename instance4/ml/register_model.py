import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# MLflow 서버 URI 설정
mlflow.set_tracking_uri("http://3.39.68.171:30003")

# 데이터 로드
data = load_iris()
X = data.data
y = data.target

# 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 모델 학습
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 입력 예제 생성
input_example = X_test[0].reshape(1, -1)  # 첫 번째 테스트 샘플을 입력 예제로 사용

# MLflow에서 모델 등록
with mlflow.start_run():
    mlflow.log_param("n_estimators", 100)  # 파라미터 로깅
    mlflow.log_metric("accuracy", model.score(X_test, y_test))  # 메트릭 로깅
    mlflow.sklearn.log_model(model, "model", input_example=input_example)  # 모델 로깅

print("모델이 MLflow에 등록되었습니다.")

