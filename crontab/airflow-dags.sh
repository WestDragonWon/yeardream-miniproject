#!/bin/bash

# 로컬 DAGS 폴더 경로
LOCAL_DAGS_PATH="/home/ubuntu/yeardream-miniproject/k8s/app/workflow/airflow/dags"

# 파드 이름 및 DAGS 폴더 경로
POD_NAME=$(kubectl get pods --selector=app=airflow-webserver -o jsonpath='{.items[0].metadata.name}')
POD_DAGS_PATH="/opt/airflow/dags"

# 파드에서 로컬로 파일 복사
kubectl cp "$POD_NAME:$POD_DAGS_PATH" "$LOCAL_DAGS_PATH"
