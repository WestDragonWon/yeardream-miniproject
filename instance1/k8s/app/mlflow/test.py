import mlflow
import mlflow.sklearn
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression
import joblib

# MLflow 서버 URL 설정
mlflow.set_tracking_uri("http://10.103.36.87:8080")
mlflow.set_experiment("testjun")

# 데이터 생성
X, y = make_regression(n_samples=100, n_features=1, noise=10)

# 모델 생성
model = LinearRegression()

# MLflow Run 시작
with mlflow.start_run():
    # 모델 훈련
    model.fit(X, y)
    
    # 파라미터와 메트릭 기록
    mlflow.log_param("fit_intercept", model.fit_intercept)
    mlflow.log_metric("coefficient", model.coef_[0])

    # 모델 아티팩트 저장
    joblib.dump(model, "linear_model.pkl")
    mlflow.log_artifact("linear_model.pkl")

    # 모델을 MLflow에 저장
    mlflow.sklearn.log_model(model, "model")

print("모델 학습 및 아티팩트 로그 완료!")
