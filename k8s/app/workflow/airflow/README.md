# Kubernetes 기반 Airflow 고가용성 클러스터 구성

Kubernetes 환경에서 고가용성 Airflow 클러스터를 배포하기 위한 구성을 제공합니다.

## 목차

1. [개요](#개요)
2. [구성 요소](#구성-요소)
3. [사전 요구 사항](#사전-요구-사항)
4. [설치 방법](#설치-방법)
5. [설정](#설정)
6. [사용 방법](#사용-방법)
7. [문제 해결](#문제-해결)

## 개요
이 프로젝트는 Apache Airflow 2.9.3 버전을 기반으로 커스텀 도커 이미지를 생성하고, Kubernetes 클러스터에 배포하는 방식으로 구성되었습니다. Airflow는 데이터 파이프라인 관리와 워크플로 자동화를 지원하며, 본 프로젝트에서는 Kafka, AWS, PostgreSQL 등의 다양한 외부 시스템과 통합할 수 있는 패키지 설치 및 한국 시간대(KST)를 반영한 설정을 제공합니다.

## 구성 요소
1. **Dockerfile**: Airflow의 도커 이미지에 추가 패키지 설치 및 한국 시간대 설정을 포함한 커스텀 빌드 구성.
2. **entrypoint.sh**: Airflow 실행 전 `airflow.cfg` 파일에서 기본 시간대 설정을 자동으로 KST로 변경하는 스크립트.
3. **Kubernetes Deployment**: Airflow의 `scheduler`와 `webserver`를 각각의 Kubernetes Deployment로 배포하며, PostgreSQL 및 AWS 자격 증명을 Kubernetes `Secret`으로 관리.

## 사전 요구 사항
1. **Kubernetes 클러스터**: Airflow가 동작할 Kubernetes 클러스터가 필요합니다.
2. **Docker**: 도커 이미지 빌드를 위해 Docker가 필요합니다.
3. **PostgreSQL**: Airflow 메타데이터를 저장할 PostgreSQL 데이터베이스가 필요합니다.
4. **AWS 자격 증명**: AWS S3와 같은 AWS 리소스를 사용할 경우 자격 증명이 필요합니다.

## 설치 방법
1. Dockerfile을 사용해 커스텀 Airflow 이미지를 빌드합니다.
2. Kubernetes에 필요한 PVC(Persistent Volume Claim)를 생성합니다.
3. Kubernetes에 `scheduler` 및 `webserver`를 배포합니다.

## 설정
1. **Airflow 시간대 설정**: `entrypoint.sh`를 통해 Airflow의 시간대를 `Asia/Seoul`로 설정합니다.
2. **AWS 자격 증명**: AWS 자격 증명은 Kubernetes `Secret`으로 관리되며, 배포 시 환경 변수로 전달됩니다.
3. **PostgreSQL 설정**: PostgreSQL 연결 정보는 `ConfigMap`을 통해 설정하며, 배포 시 `SQL_ALCHEMY_CONN` 환경 변수로 전달됩니다.

## 사용 방법
1. Airflow UI에 접속하여 DAG을 관리하고 모니터링합니다.
   - 웹 브라우저에서 Airflow 웹서버가 배포된 노드의 IP 주소와 포트 30091을 입력하여 접속합니다.
   - .env의 AIRFLOW_ADMIN_USERNAME / AIRFLOW_ADMIN_PASSWORD 값을 확인하여 인증한다.
   - DAG 스케줄링 및 실행 상태를 모니터링할 수 있습니다.

## DAGs 작성할 jupyternote 사용법

1. 실행중인 pod의 서비스 노드외부ip:30092 로 접속한다. 
.env의 JUPYTER_TOKEN 값을 입력하여 보안 인증한다.
   
2. DAG 파일은 `Persistent Volume`에 저장된 경로를 통해 Kubernetes Pod에서 액세스할 수 있으며, 로그는 `logs` 폴더에 기록됩니다.

## 문제 해결

### 1. **airflow-webserver**
- **EFS 마운트 / PostgreSQL 연결**:  
  Airflow 웹서버는 EFS와 PostgreSQL을 사용하여 로그 저장 및 메타데이터 관리 작업을 처리합니다. EFS는 PersistentVolumeClaim(PVC)을 통해 마운트되며, PostgreSQL 연결 정보는 Kubernetes Secret을 사용해 안전하게 전달됩니다.

### 2. **airflow-scheduler**
- **DAG 경로 설정 및 PVC 마운트**:  
  Airflow는 기본적으로 DAG 파일을 `/opt/airflow/dags/` 경로에서 찾습니다. 이를 위해 PersistentVolumeClaim(PVC)을 DAG 파일 경로로 마운트해야 합니다. 이를 통해 DAG 파일이 공유되어 스케줄링과 작업 실행이 원활하게 진행됩니다.

### 3. **airflow-worker**
- **Redis 연결**:  
  Airflow 워커는 Celery Executor를 통해 Redis와 연결됩니다. 하지만 Redis 클러스터와는 아직 호환되지 않아 기본적인 Redis 연결 방식만 사용할 수 있습니다.

---

### Airflow의 Fernét 암호화 키 사용처

1. **Connections (연결 정보)**:  
   Airflow에서 외부 서비스와의 연결을 관리하기 위해 설정된 Connections에는 API 키, 비밀번호, 토큰 등의 민감한 정보가 포함될 수 있습니다. Fernét 암호화 키가 설정된 경우, 이러한 민감한 정보는 암호화되어 저장되며 필요할 때만 복호화됩니다.

2. **Variables (변수 값)**:  
   Variables 기능을 통해 DAG 또는 태스크에서 사용되는 전역 변수를 설정할 수 있습니다. 여기에는 경로, 비밀번호 등 민감한 정보가 저장될 수 있으며, Fernét 암호화 키가 설정되면 해당 정보는 암호화된 상태로 데이터베이스에 저장됩니다.

3. **XCom (Cross-Communication 데이터)**:  
   DAG 태스크 간의 데이터 교환에 사용되는 XCom 값도 Fernét 키로 암호화될 수 있습니다. 이를 통해 태스크 간 전송되는 데이터의 보안을 강화할 수 있습니다.

---

### 초기화 과정

Airflow를 처음 설치하고 데이터베이스를 설정할 때 `airflow db init`을 사용하여 데이터베이스를 초기화해야 합니다. 그러나 이를 모르고 `airflow db migrate` 명령어를 사용할 경우, 데이터베이스가 아직 초기화되지 않았기 때문에 필요한 테이블이나 스키마가 누락되어 오류가 발생할 수 있습니다.

따라서 데이터베이스가 처음 설치되었을 때는 반드시 `airflow db init` 명령어를 사용하여 초기화를 진행해야 하며, 데이터베이스가 이미 설정되어 있는 경우에만 `airflow db migrate` 명령어를 사용하여 스키마를 업데이트해야 합니다.

---

### 다중 PVC 문제

여러 PVC를 하나의 PV에 연결할 수 없기 때문에 여러 Pod이 하나의 PVC에 연결되도록 구성해야 합니다. 이 문제는 다중 Pod이 단일 PVC에 연결되면 해결됩니다.

---

### Celery 버전 확인 및 Redis 연결

Airflow에서 Celery Executor를 사용하고 있으며, 현재 Redis와의 연결이 가능합니다. 하지만 Redis 클러스터와는 아직 호환되지 않으며, 이는 Celery와 Redis 클러스터 간의 호환성 문제로 인해 발생한 것으로 보입니다.

---

### 스케줄러와 워커 설정

- **Scheduler**: Role-binding 설정을 성공적으로 마쳤습니다.
- **Worker**: Celery Executor 설정이 추가로 필요합니다.

---

### DAG 폴더 동기화 및 Jupyter Notebook 연동

DAG 폴더를 로컬과 동기화하기 위해 `rsync`를 사용한 동기화 방법을 선택했습니다. 직접 EFS를 마운트하는 방법은 설치 과정이 복잡하여 대체 방법으로 `rsync`를 활용해 로컬 폴더와의 동기화를 해결했습니다. 이를 통해 Jupyter Notebook을 사용하여 작성한 DAG 소스코드 추적이 용이하게 이루어질 수 있습니다.

Airflow 이미지를 새로 빌드하여 위의 문제들을 해결하고 배포하였습니다.


---


Airflow에서 다양한 외부 서비스와의 연결을 관리하기 위해 Connections를 설정합니다.
예를 들어, AWS, Google Cloud, PostgreSQL, MySQL 등 외부 데이터베이스나 클라우드 서비스와의 연결을 위해 필요한 API 키, 사용자 비밀번호, 토큰 등이 저장됩니다.
이러한 연결 정보는 Airflow의 메타데이터 데이터베이스에 저장되는데, 암호화 키가 설정되어 있으면 비밀번호나 API 키 같은 민감한 정보는 암호화되어 저장됩니다.
암호화된 데이터는 필요할 때만 Fernét 키를 사용하여 복호화되어 사용됩니다.
Variables (변수 값)

Airflow에서는 Variables라는 기능을 통해 DAG나 태스크에서 사용할 수 있는 전역 변수들을 설정할 수 있습니다.
이 변수에는 서비스 연결 정보, 경로, 비밀번호 등의 민감한 정보가 저장될 수 있습니다.
설정된 Fernét 암호화 키는 이러한 변수가 데이터베이스에 저장될 때 암호화해 주며, FERNET_KEY가 설정되어 있지 않으면 민감한 정보가 암호화되지 않고 평문으로 저장됩니다.
XCom (Cross-Communication 데이터)

DAG의 태스크 간에 데이터를 주고받는 데 사용되는 XCom 값도 암호화될 수 있습니다.
이를 통해 태스크 간 전달되는 데이터가 안전하게 보호됩니다.

- 암호와 키 생성 (예시)
```
pip install cryptography
python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
aT5C3O9_YDFztF7NIlkjhg7VBH3hvZLlWXYPcvGr6Hk=
```



---
kubectl exec -it airflow-webserver-69f896489f-q859h -- celery --version
Defaulted container "airflow-webserver" out of: airflow-webserver, initialize-airflow-db (init)
5.4.0 (opalescent)

celery excutor / redis와 연결하는데 필요한 모듈
-> redis 클러스터와는 아직 호환이안됨 망할 ㅠㅠ 아까운 내 시간

worker 작동방식


---
scheduler // role-binding 성공
worker // excutor 설정 필요
