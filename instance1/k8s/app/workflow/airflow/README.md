# Kubernetes 기반 Airflow 고가용성 클러스터 구성

Kubernetes 환경에서 고가용성 Airflow 클러스터를 배포하기 위한 구성을 제공합니다.

## 목차

1. [개요](#개요)
2. [구성 요소](#구성-요소)
3. [사전 요구 사항](#사전-요구-사항)
4. [설치 방법](#설치-방법)
5. [설정](#설정)
6. [사용 방법](#사용-방법)
7. [백업 및 복원](#백업-및-복원)
8. [모니터링](#모니터링)
9. [문제 해결](#문제-해결)


## airflow 사용법

실행중인 pod의 서비스 노드외부ip:30091 로 접속한다. 
.env의 AIRFLOW_ADMIN_USERNAME / AIRFLOW_ADMIN_PASSWORD 값을 확인하여 인증한다.

추가한 dag를 airflow 웹서버 pod내에 /opt/airflow/dags 파일 디렉토리내에서 다음 명령어실행 dags `airflow dags list`

## DAGs 작성할 jupyternote 사용법

실행중인 pod의 서비스 노드외부ip:30092 로 접속한다. 
.env의 JUPYTER_TOKEN 값을 입력하여 보안 인증한다.

## 개요


## 구성 요소

- 

## 사전 요구 사항




## 설치 방법


## 설정


## 사용 방법


## 백업 및 복원


## 모니터링

## 보안

## 작업순서

사용한 DB는 Redis / PostgreSQL

1. airflow-webserver
EFS 마운트 / postgresql 연결

2. airflow-schedule
Airflow는 기본적으로 DAG 파일을 /opt/airflow/dags/ 경로에서 찾습니다. 따라서 PersistentVolumeClaim을 DAG 파일 경로로 마운트하여 사용해야 합니다.

3. airflow-worker
redis 연결

Airflow의 Fernét 암호화 키 사용처
Connections (연결 정보)

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


현재 initContainers에서 Airflow 데이터베이스 마이그레이션(migrate)을 수행하도록 설정되어 있는데, 데이터베이스를 처음 초기화할 때는 migrate 대신 init을 사용해야 합니다.

따라서 airflow db migrate 대신 airflow db init을 사용하면 Airflow 데이터베이스 초기화를 수행할 수 있습니다.



----

동시에 실행하면 왜 안되지??? 
- pvc - pv 문제였고 다중pvc -> pv1 불가 다중pod -> pvc1 가능


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


---

dags 폴더를 local과 동기화 // 쉽게 dag작성하기
-> jupyternotebook 파드를 생성하여 연결

소스코드가 git에 자동으로 올라가게하려면 로컬과 폴더내용도 동기화해야하는데
efs를 직접 마운트하려고했더니 efs util 설치가 복잡하고 까다로워서
pod 폴더를 로컬로 rsync로 동기화하는 방법을 선택

해결을 위해 airflow image를 새로 빌드하여 배포
