import mlflow

mlflow.set_tracking_uri("http://10.108.228.103:8080")  # MLflow 서버 URL 설정
mlflow.set_experiment("test_experiment")  # 실험 이름 설정

with mlflow.start_run():
    mlflow.log_param("param1", 5)
    mlflow.log_metric("metric1", 0.87)
