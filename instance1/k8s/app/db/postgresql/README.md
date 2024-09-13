# Kubernetes 기반 PostgreSQL 고가용성 클러스터

이 프로젝트는 Patroni를 사용하여 Kubernetes 환경에서 고가용성 PostgreSQL 클러스터를 배포하기 위한 구성을 제공합니다.

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

## 개요

이 PostgreSQL 클러스터 설정은 Patroni를 사용하여 클러스터 관리를 하고 Kubernetes StatefulSet을 활용하여 고가용성과 확장성을 제공합니다. 읽기 전용 복제본, 자동 확장, 백업 및 보안 정책에 대한 구성이 포함되어 있습니다.

## 구성 요소

- PostgreSQL 13
- 클러스터 관리를 위한 Patroni
- 주 PostgreSQL 인스턴스를 위한 Kubernetes StatefulSet
- 읽기 전용 복제본을 위한 Kubernetes Deployment
- 읽기 전용 복제본의 자동 확장을 위한 Horizontal Pod Autoscaler
- 영구 데이터 저장을 위한 EFS 스토리지
- 보안을 위한 네트워크 정책
- CronJob을 사용한 예약 백업

## 사전 요구 사항

- Kubernetes 클러스터
- 클러스터와 통신하도록 구성된 kubectl
- 클러스터에 설치된 EFS CSI 드라이버
- (선택사항) 쉬운 배포를 위한 Helm

## 설치 방법

1. 이 저장소를 클론합니다:
   ```
   git clone <저장소-URL>
   cd postgresql-ha-cluster
   ```

2. 필요한 시크릿을 생성합니다: # 현재 name db에 비밀번호 지정 중
   ```
   kubectl create secret generic db \
     --from-literal=POSTGRES_PASSWORD=<postgres-비밀번호> \
     --from-literal=POSTGRES_REPLICATION_PASSWORD=<복제-비밀번호>
   ```

3. 구성을 적용합니다:
   ```
   kubectl apply -f postgres-base-config.yaml
   kubectl apply -f postgres-cluster.yaml
   kubectl apply -f postgres-readonly.yaml
   kubectl apply -f postgres-security.yaml
   kubectl apply -f postgres-backup.yaml
   ```

## 설정

- `postgres-config`을 수정하여 PostgreSQL 및 Patroni 설정을 조정합니다.
- 필요에 따라 `postgresql.yaml` 및 `postgres-readonly.yaml`의 리소스 요청 및 제한을 조정합니다.
- 필요한 경우 `postgres-backup.yaml`의 백업 일정을 수정합니다.

## 사용 방법

- 주 PostgreSQL 인스턴스에 연결:
  ```
  kubectl exec -it postgres-cluster-0 -- psql -U postgres
  ```

- 읽기 전용 복제본에 연결:
  ```
  kubectl exec -it <읽기전용-팟-이름> -- psql -U postgres
  ```

## 백업 및 복원

백업은 CronJob을 사용하여 매일 예약됩니다. 수동 백업을 수행하려면:

```
kubectl create job --from=cronjob/postgres-backup manual-backup
```

복원 프로세스는 특정 요구 사항과 클러스터 상태에 따라 다릅니다.

## 모니터링

PostgreSQL 클러스터 모니터링을 위해 Prometheus와 Grafana 설정을 고려 쉬운 배포를 위해 다음 Helm 차트를 사용할 수 있음.

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack
```

## 문제 해결

- 팟 상태 확인: `kubectl get pods`
- 팟 로그 보기: `kubectl logs <팟-이름>`
- Patroni 로그: `kubectl logs <팟-이름> -c patroni`

더 자세한 문제 해결은 Patroni와 PostgreSQL 문서를 참조