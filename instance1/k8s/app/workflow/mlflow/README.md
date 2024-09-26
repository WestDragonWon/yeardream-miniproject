
# MLflow in kube

# 목차

1. [개요](개요)
2. [S3 연결](#s3-연결)
3. [DB 연결](#db-연결)
4. [실행방법](#실행방법)

## 개요

Kubernetes 환경에서 MLflow를 사용하기 위한 구성을 제공합니다.

- 스케일링: Kubernetes의 오토 스케일링 기능을 활용하여 MLflow 서버를 동적으로 스케일링할 수 있음.

- 고가용성: MLflow 서비스를 여러 인스턴스로 배포하여 고가용성을 보장할 수 있음

- 자동화: CI/CD 파이프라인과 통합하여 머신러닝 모델의 자동 배포 및 업데이트를 쉽게 수행할 수 있음.

- 리소스 관리: Kubernetes의 리소스 관리 기능을 통해 MLflow의 CPU 및 메모리 사용량을 최적화할 수 있음.

내구성, 고가용성이 보장된 Postgres에 메타 데이터를 저장하고, S3에 아티팩트를 저장하도록 하였습니다.

![alt text](<img/Pasted image 20240924144753.png>)

## 사전 요구 사항

- Kubernetes 클러스터
- S3 Access ID, Secret Access Key
- Kubernetes상에 띄워진 Postgres

## 구성 요소

- MLflow 환경을 만들기 위한 Deployment, Service

## 설치 방법


저장소를 클론합니다. 파일은 instance1/k8s/app/workflow/mlflow에 위치합니다.
 ```
   git clone https://github.com/WestDragonWon/yeardream-miniproject.git
   cd instance1/k8s/app/workflow/mlflow
   ```

AWS ACCESS KEY ID 및 AWS SECRET ACCESS KEY, POSTGRES USER, POSTGRES PASSWORD, S3 아티팩트 저장소 경로를 .env파일에 저장해야합니다.
    ```
    AWS_ACCESS_KEY_ID=~~~~~~~
    AWS_SECRET_ACCESS_KEY=~~~~~~~~
    MLFLOW_S3_ARTIFACT_ROOT=s3://~~~
    POSTGRES_USER=<유저이름>
    POSTGRES_PASSWORD=<P.W>
    형식으로
    ```

### S3 연결

**쿠버 삭제하고 다시 설치하면 사라지는 설정이므로 다시 입력이 필요함**

`export MLFLOW_S3_ARTIFACT_ROOT=s3://team06-mlflow-feature #연결할 버킷 이름`

- S3 연결을 위해 AWS 액세서 ID, key 등 .env의 내용을 SECRET으로 만들어야합니다.

`kubectl create secret generic 지정한이름 --from-env-file=.env`


## DB 연결

```
"--backend-store-uri", "postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@postgres:5432/mlops"
```

postgresql:// : postgre 쓰겠다고 명시하는 부분

/mlops : DB 이름 지정

## 실행방법

아래 url로 접속

http://<EC2_public_ip>:30003

## Mlflow 시각화, 성능 테스트, 모델 레지스트리 및 배포 자동화

### Tracking API

- mlflow.start_run(): 이 함수를 통해 새로운 실행(run)을 함.
  훈련 중에 사용한 하이퍼파라미터, 훈련 데이터, 모델 아키텍처   등의 정보를 기록 가능함.

- mlflow.log_metric(): 훈련 중에 얻은 성능 지표(예: 정확도, 손실 값)를 기록. 여러 지표를 기록해서 모델의 성능을 종합적으로 평가할 수 있음.

- mlflow.log_artifact(): 훈련된 모델 파일, 그래프, 데이터 시각화등을 이 함수로 저장 가능함. 

### 모델 레지스트리

        # 모델 레지스트리에 등록
        model_uri = f"runs:/{mlflow.active_run().info.run_id}/{model_path}"
        mlflow.register_model(model_uri, "IrisModel")

테스트용으로 만든 간단한 모델의 코드 일부.

같은 이름으로 모델을 지정하면 mlflow가 자동으로 버저닝을 해준다.