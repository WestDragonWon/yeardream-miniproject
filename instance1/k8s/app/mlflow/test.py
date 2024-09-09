import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# MLflow Tracking URI 설정
mlflow.set_tracking_uri("http://3.39.68.171:30003")  # 적절한 IP와 포트로 변경하세요.

try:
    # 데이터 로드
    iris = load_iris()
    X = iris.data
    y = iris.target
except Exception as e:
    print("데이터 로드 중 에러 발생:", e)
    exit(1)

# 데이터 분할
try:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
except Exception as e:
    print("데이터 분할 중 에러 발생:", e)
    exit(1)

# 모델 학습
try:
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
except Exception as e:
    print("모델 학습 중 에러 발생:", e)
    exit(1)

# MLFLOW에 모델 등록
with mlflow.start_run():
    # 모델 저장
    try:
        mlflow.sklearn.log_model(model, "random_forest_model")
    except Exception as e:
        print("모델 저장 중 에러 발생:", e)
        exit(1)

    # 파라미터와 메트릭 로그
    try:
        mlflow.log_param("n_estimators", model.n_estimators)
        mlflow.log_param("max_depth", model.max_depth)
        mlflow.log_metric("accuracy", model.score(X_test, y_test))
    except Exception as e:
        print("파라미터 또는 메트릭 로그 중 에러 발생:", e)
        exit(1)

    # 모델 등록
    model_uri = "runs:/{}/random_forest_model".format(mlflow.active_run().info.run_id)
    
    try:
        mlflow.register_model(model_uri, "IrisRandomForestModel")  # 모델 이름을 변경할 수 있습니다.
        print("모델이 MLFLOW에 등록되었습니다.")
    except Exception as e:
        print("모델 등록 중 에러 발생:", e)
