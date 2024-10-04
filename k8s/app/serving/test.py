import mlflow
import mlflow.sklearn
import pandas as pd
import boto3
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# S3에서 파일 다운로드
s3 = boto3.client('s3')
bucket_name = 'team06-mlflow-feature'  # S3 버킷 이름
s3_object_name = 'iris.csv'  # S3에 저장된 파일 이름
local_file_path = '/home/ubuntu/yeardream-miniproject/instance1/k8s/app/serving/data/iris.csv'  # 다운로드할 로컬 파일 경로

# S3에서 파일 다운로드
s3.download_file(bucket_name, s3_object_name, local_file_path)

# MLflow 서버 URL 설정
mlflow.set_tracking_uri("http://10.103.73.87:8080")
mlflow.set_experiment("testjun")

# 데이터셋 로드
data = pd.read_csv(local_file_path)  # 로컬에서 CSV 파일 로드
X = data.drop('Species', axis=1)  # 'Species' 열을 제외한 모든 열
y = data['Species']  # 'Species' 열

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

# 다운로드한 파일 삭제 (선택 사항)
os.remove(local_file_path)
