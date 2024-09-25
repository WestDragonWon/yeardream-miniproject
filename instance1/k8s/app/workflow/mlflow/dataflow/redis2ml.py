import pandas as pd
from rediscluster import RedisCluster
import json
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Redis 클러스터 접속 정보
startup_nodes = [{"host": "192.168.182.16", "port": "6379"}]  # Redis 서비스의 ClusterIP
redis_client = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

# Redis에서 데이터 불러오기
data = []
index = 0

while True:
    row = redis_client.get(f"row:{index}")
    if row is None:
        break
    data.append(json.loads(row))
    index += 1

# DataFrame으로 변환
iris_data = pd.DataFrame(data)

# MLflow 설정
mlflow.set_tracking_uri("http://10.103.73.87:8080")  # MLflow 서버 URL
mlflow.set_experiment("iris_experiment")  # 실험 이름 설정

# MLflow 실행 시작
mlflow.start_run()

# 특징(X)과 레이블(y) 분리
X = iris_data.drop(columns='Species')
y = iris_data['Species']

# 훈련 데이터와 테스트 데이터로 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

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

print("Model has been trained and logged to MLflow.")
