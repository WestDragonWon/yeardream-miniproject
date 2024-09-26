# Yeardream Miniproject - MLOps & DataPipeline System

## License
이 프로젝트는 MIT License에 따라 배포됩니다.
다음을 참고 해주세요. [LICENSE](./LICENSE)

This project is licensed under the MIT License
see the [LICENSE](./LICENSE) file for details.

## Team Composition - GitHub IDs
- **Team Leader**: 서용원 - WestDragonWon
- **Team Members**:
  - 변준호 - Loafingcat
  - 김민규 - xxxmingyu
  - 이시형 - FirstBright
- **Contributors**:
  - 전영남 - 00nam11
  - 강재국 - kangjaeguk

## 프로젝트 개요
이 프로젝트는 **MLOps**와 **데이터 파이프라인**을 통합한 견고한 시스템을 구축하는 것을 목표로 합니다. **AWS**와 **Kubernetes**를 기반으로 머신러닝 워크플로우 및 데이터 처리 파이프라인을 자동화하여, 머신러닝 모델의 확장과 대규모 데이터 처리를 위한 프로덕션 수준의 솔루션을 제공합니다.

## 프로젝트 목표

1. 머신러닝 모델을 프로덕션에 배포하는 자동화된 **MLOps** 시스템 구축.
2. 대량의 데이터를 처리할 수 있는 안정적이고 확장 가능한 **데이터 파이프라인** 구축.
3. 워크플로우 전반에 걸쳐 보안과 데이터 영속성을 보장.
4. Kubernetes와 클라우드 네이티브 도구를 적용하여 고가용성과 장애 허용성 달성.
### 5. 단순히 도구를 이용해보는 실습이 아닌 / 서비스를 배포하기 위한 도구들의 작동 방식과 각각의 주요 옵션들에 대한 이해를 기반으로 이후 원하는 서비스를 제약없이 구축 할 수 있는 능력을 기르기.


## 주요 기능


## 기술 스택
### Base System
- **Cloud Provider**: AWS
- **Container Orchestration**: Kubernetes

### Data Pipeline
- **Workflow Management**: Apache Airflow
- **Data Message Que**: Apache Kafka
- **Data Processing**: Apache Spark, S3 Glue, ELK 
- **Data DB & Storage**: Redis, MongoDB, AWS-EBS-gp3, AWS-EFS, AWS-S3
- **Data Engineering Automation**: Bash sh + Crontab, AWS CLI
- **Monitoring**: K8s-Dashboard, Prometheus, Grafana

### Data Pipeline
- **Workflow** Management: Apache Airflow
- **Data Message Queue**: Apache Kafka
- **Data Processing**: Apache Spark, S3 Glue, ELK, AWS Athena
- **Data DB & Storage**: Redis, MongoDB, PostgreSQL, AWS-EBS-gp3, AWS-EFS, AWS-S3
- **Data Engineering Automation**: Bash sh + Crontab, AWS CLI, GitHub
### Infrastructure
- **Load Balancer**: nginx-ingress-controller, metallb
- **Containerization**: Docker, DockerHub
### Monitoring & Alerts
- **Monitoring**: K8s-Dashboard, Prometheus, Grafana
- **Alerting**: Alertmanager
### Version Control
- **Version Control**: GitHub


### MLOps
- **MLOps**: MLFlow 
- **Model Serving**: FastAPI
- **data storage**: Amazon S3(artifact), PostgreSQL(meta)
- **CI/CD**: GitHub Actions

## 프로젝트 진행 방식

각 디렉토리에서 관리되는 리소스나 도구는 이 프로젝트의 중요한 부분이며, 해당하는 `README.md` 파일을 통해 각각의 역할과 사용법을 확인할 수 있습니다.

## 프로젝트 일정
- **1차 스프린트**: 프로젝트 계획 & K8s 기반 구축 (8월 28일 - 9월 3일)
- **2차 스프린트**: MLOps 구축 (9월 3일 - 9월 12일)
- **3차 스프린트**: 데이터 파이프라인 구축 (9월 13일 - 9월 23일)
- **4차 스프린트**: 전체 시스템 고도화 (9월 25일 - 9월 30일)
- **5차 스프린트**: 전체 시스템 테스트 및 디버깅 (10월 1일 - 10월 4일)
- **6차 스프린트**: 포트폴리오 제작 및 배포 (10월 7일 - 10월 10일)


---


## 목차
### 디렉토리와 `README.md` 파일에 대한 링크를 제공합니다.
1. [aws](./instance1/aws/README.md)
    - [athena](./instance1/aws/athena/README.md)
    - [awscli](./instance1/aws/awscli/README.md)
    - [glue](./instance1/aws/glue/README.md)
2. [crontab](./instance1/crontab/README.md)
3. [docs](./instance1/docs/README.md)
4. [k8s](./instance1/k8s/app/README.md)
   - [app](./instance1/k8s/app/README.md)
     - [db]
       - [elasticsearch]
       - [mongodb](./instance1/k8s/app/db/mongodb/README.md)
       - [postgresql](./instance1/k8s/app/db/postgresql/README.md)
       - [redis](./instance1/k8s/app/db/redis/README.md)
     - [monitoring]
       - [alertmanager](./instance1/k8s/app/monitoring/README.md)
     - [processing](./instance1/k8s/app/processing/README.md)
       - [kafka](./instance1/k8s/app/processing/kafka/README.md)
       - [spark](./instance1/k8s/app/processing/spark/README.md)
     - [serving](./instance1/k8s/app/serving/README.md)
     - [system]
       - [aws-ebs-efs](./instance1/k8s/app/system/README.md)
       - [dashboard](./instance1/k8s/app/system/dashboard/helm/README.md)
       - [helm]
       - [metallb](./instance1/k8s/app/systeam/metallb/README.md)
       - [namespace](#system)
       - [nginx-ingress-controller](#system)
     - [workflow](./instance1/k8s/app/workflow/README.md)
       - [airflow](./instance1/k8s/app/workflow/airflow/README.md)
       - [mlflow](./instance1/k8s/app/workflow/mlflow/README.md)
   - [resources](#resources)
     - [configmap](#resources)
     - [namespace]
     - [pv](#resources)
     - [role]
     - [secret](#resources)
     - [serviceaccount]
     - [storageclass](./instance1/k8s/resources/storageclass/README.md)
     - [job/cronjob]


---

## License
이 프로젝트는 MIT License에 따라 배포됩니다.
다음을 참고 해주세요. [LICENSE](./LICENSE)

This project is licensed under the MIT License
see the [LICENSE](./LICENSE) file for details.