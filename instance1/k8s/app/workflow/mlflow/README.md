# MLflow in kube

# 목차

1. [개요](#개요)
2. [S3 연결](#s3-연결)
3. [DB 연결](#db-연결)
4. [실행방법](#실행방법)

## 개요

- 스케일링: Kubernetes의 오토 스케일링 기능을 활용하여 MLflow 서버를 동적으로 스케일링할 수 있음.
- 고가용성: MLflow 서비스를 여러 인스턴스로 배포하여 고가용성을 보장할 수 있음
- 자동화: CI/CD 파이프라인과 통합하여 머신러닝 모델의 자동 배포 및 업데이트를 쉽게 수행할 수 있음.
- 리소스 관리: Kubernetes의 리소스 관리 기능을 통해 MLflow의 CPU 및 메모리 사용량을 최적화할 수 있음.


## S3 연결

export MLFLOW_S3_ARTIFACT_ROOT=s3://team06-mlflow-feature #연결할 버킷 이름


- S3 연결을 위해 AWS 액세서 ID, key 포함한 secret 생성

		kubectl create secret generic [지정한이름] --from-env-file=.env

## DB 연결

	"--backend-store-uri", "postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@postgres:5432/mlops"

postgresql:// : postgre 쓰겠다고 명시하는 부분

/mlops : DB 이름 지정

## 실행방법

아래 url로 접속

http://<EC2_public_ip>:30003