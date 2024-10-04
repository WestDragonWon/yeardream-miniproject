# Kubernetes 기반 Redis 고가용성 클러스터 구성

Kubernetes 환경에서 고가용성 Redis 클러스터를 배포하기 위한 구성을 제공합니다.

## 목차

1. [개요](#개요)
2. [구성 요소](#구성-요소)


## 개요

- 프로젝트 내에서 Redis Cluster는 MongoDB의 ReplicaSet과 연계되어 **웹 개발 및 운영** 부서에서 사용됩니다.
- **MongoDB**는 주로 영구 저장이 필요한 데이터를 관리하며, **Redis**는 로그인 세션과 같이 **짧은 시간 동안 사용**되거나 **캐싱**을 위한 데이터를 처리합니다.
- **MongoDB**와 **Redis**는 **상호보완적인 관계**로 구축되어, 비정형 데이터를 처리하고 데이터의 **고가용성**을 보장합니다.

## 구성 요소

- **Redis 7.0.5** 이미지/버전
- **StatefulSet 구성**: 각 파드별로 **자동 프로비저닝**되는 **gp3 EBS**를 사용하기 위해 **EBS CSI 드라이버** 및 권한 설정 포함
- **네트워크 정책**: 보안을 위한 **네트워크 정책** 설정

Redis 클러스터는 **3개의 인스턴스**로 구성되어 고가용성과 강력한 분산 처리 능력을 제공합니다. 기본적으로 권장되는 구성은 **3개의 마스터**와 **3개의 슬레이브**로 이루어진 **6개의 인스턴스**입니다. 그러나 현재 리소스 제약을 고려하여 **효율적인 동작**을 목표로 설정되었습니다.

### 클러스터 설계:
- **gp3 볼륨**을 사용해 **리전별로 백업 복제** 및 **복원**이 가능합니다.
- **3개의 마스터 노드**로 구성된 클러스터는 **1~2 서버 또는 Pod 장애**가 발생하더라도 **데이터 무결성**을 유지합니다.
- Kubernetes를 활용해 장애 발생 시 **즉시 서비스가 재개**될 수 있도록 설계되었습니다.

- **replicas: 3**
  - 3개의 **마스터 노드**로 Redis 클러스터를 구성합니다. 각 마스터 노드는 고유한 상태를 가지며, 데이터를 복제하지 않습니다. 클러스터에 여러 파드가 있어도 각 파드는 고유한 **Persistent Volume**을 가집니다.

- **nodeSelector: worker**
  - Redis 파드가 **worker 노드**에서만 실행되도록 설정되었습니다. 특정 노드 타입에만 배포하고 싶을 때 `nodeSelector`를 사용할 수 있습니다.

- **volumeMounts**
  - Redis 파드에서 `/data` 디렉토리에 **Persistent Volume**을 마운트하여, Redis가 데이터를 영구적으로 저장할 수 있도록 합니다.

- **Redis 설정 (command와 args)**
  - **Redis 서버 실행**: `redis-server` 명령어를 사용하여 Redis 서버를 시작합니다.
  - **클러스터 모드 활성화**: `--cluster-enabled yes` 플래그를 통해 Redis 클러스터 모드를 활성화합니다.
  - **클러스터 설정 파일**: `--cluster-config-file /data/nodes.conf`는 Redis 클러스터 노드 정보가 저장될 파일 경로를 지정합니다.
  - **클러스터 노드 타임아웃**: `--cluster-node-timeout 5000`은 클러스터 내 노드 간 통신의 타임아웃을 설정합니다.
  - **데이터 영속성**: `--appendonly yes`와 `--appendfsync everysec`을 통해 Redis 데이터가 **AOF(Append Only File)**로 저장되며, 매 초마다 데이터가 파일에 동기화됩니다.
  - **데이터 스냅샷**: `--save 900 1`, `--save 300 10`, `--save 60 10000` 설정은 지정된 시간 간격마다 변경 사항을 스냅샷으로 저장하는 방식입니다.

- **readinessProbe**
  - `readinessProbe`는 Redis 파드가 **정상적으로 실행 중**인지 확인하는데 사용됩니다. 여기서는 `redis-cli ping` 명령어를 사용해 Redis가 응답하는지 확인합니다.

- **Persistent Volume Claim (PVC)**
  - `volumeClaimTemplates`는 각 Redis 파드에 **5Gi의 스토리지**를 할당하며, 한 파드에서만 쓰기가 가능한 `ReadWriteOnce` 모드를 사용합니다.


## 사전 요구 사항

- **Kubernetes 클러스터**: Redis가 배포될 준비된 환경
- **kubectl**: 클러스터와 통신할 수 있도록 구성된 도구
- **EBS CSI 드라이버**: Kubernetes 클러스터에 설치되어 있어야 합니다.

## 설치 방법

1. **Redis 설치**:
   - redis.yml파일을 참고하여 Redis를  StatefulSet으로 배포합니다. 


2. **클러스터 구성**:
    - 파드에 접속하여 아래 명령어를 참고하여 클러스터를 구성합니다.
    - DNS로 연결이 가능하려면 특정 버전 이상의 redis 이미지가 필요합니다.
```
kubectl exec -it <pod> /bin/bash

redis-cli -h redis-cluster-0.redis-cluster.default.svc.cluster.local -p 6379 FLUSHALL
redis-cli -h redis-cluster-0.redis-cluster.default.svc.cluster.local -p 6379 CLUSTER RESET HARD

redis-cli -h redis-cluster-1.redis-cluster.default.svc.cluster.local -p 6379 FLUSHALL
redis-cli -h redis-cluster-1.redis-cluster.default.svc.cluster.local -p 6379 CLUSTER RESET HARD

redis-cli -h redis-cluster-2.redis-cluster.default.svc.cluster.local -p 6379 FLUSHALL
redis-cli -h redis-cluster-2.redis-cluster.default.svc.cluster.local -p 6379 CLUSTER RESET HARD

redis-cli --cluster create redis-cluster-0.redis-cluster.default.svc.cluster.local:6379 \
                             redis-cluster-1.redis-cluster.default.svc.cluster.local:6379 \
                             redis-cluster-2.redis-cluster.default.svc.cluster.local:6379 --cluster-replicas 0
```
---

## 설정

1. **StatefulSet Replica 설정**:
   - 기본적으로 3개의 Redis 마스터 인스턴스와 3개의 슬레이브 인스턴스로 클러스터를 구성합니다.
   - 이를 통해 **수평 확장** 및 **고가용성**을 보장합니다.
   - 이 프로젝트에선 가용한 인스턴스 제한으로 3개의 마스터로만 구성되어 이용되었습니다.
     - 이로인해 마스터 3개의 노드가 동시에 문제가 발생하면 클러스터 구성이 끊기는 문제가 있습니다.

2. **Redis 설정**:
   - 각 인스턴스는 **Redis 설정 파일**을 통해 클러스터 모드로 작동하도록 구성합니다.
   - 마스터와 슬레이브 간의 **데이터 복제** 및 **Failover** 설정이 포함됩니다.

---

## 사용 방법

1. **kubectl 명령어**를 통해 Redis 클러스터의 상태를 확인하고 관리합니다.
   - Pod 상태 확인, 서비스 재시작, 레플리카 확장 등의 작업을 수행할 수 있습니다.
   
2. **Redis 클라이언트**를 사용하여 클러스터에 연결하고 데이터를 읽고 쓸 수 있습니다.

---

## 백업 및 복원

---

## 모니터링

1. **Prometheus 및 Grafana**를 사용하여 Redis 클러스터의 상태를 모니터링합니다.
   - CPU, 메모리 사용량, 네트워크 트래픽 및 데이터 복제 상태를 실시간으로 모니터링합니다.
   
2. **Alertmanager**와 연동하여 Redis 클러스터의 문제가 발생할 경우 **알림**을 받습니다.

---

## Redis 구성 방식과 장단점

Redis를 Kubernetes에서 구성하는 다양한 방식과 그에 따른 **장단점**을 소개합니다.

### 1. **단일 노드 Redis 구성**

단일 인스턴스의 Redis 서버를 사용하는 방식입니다.

#### 장점:
- **구성 간단**: 단일 노드이므로 관리와 설정이 매우 간단합니다.
- **저렴한 비용**: 추가 인스턴스 없이 하나의 Redis 인스턴스만 사용하므로 리소스 비용이 적습니다.

#### 단점:
- **데이터 손실 위험**: 장애가 발생할 경우, Redis 데이터가 모두 손실될 위험이 있습니다.
- **고가용성 부재**: 단일 노드 장애 시 전체 서비스가 중단될 수 있습니다.

---

### 2. **Master-Slave 구성 (Replica 구성)**

하나의 **Master Redis 노드**와 여러 **Slave 노드**를 두어 데이터를 복제하는 방식입니다.

#### 장점:
- **읽기 성능 향상**: **Slave 노드**들이 **읽기 요청**을 처리하므로 읽기 성능이 향상됩니다.
- **데이터 복제**: 데이터를 **Slave 노드**에 복제하여 **데이터 손실 위험**을 줄일 수 있습니다.

#### 단점:
- **쓰기 성능 제한**: **Master 노드**에서만 **쓰기 작업**이 이루어지므로, 쓰기 성능은 여전히 제한적입니다.
- **Failover 수동 처리**: Master 노드가 장애를 일으키면 Slave 노드를 수동으로 승격해야 하는 번거로움이 있습니다.

---

### 3. **Redis Sentinel 구성**

Redis **Sentinel**은 장애 복구 및 노드 모니터링을 제공하는 구성 방식입니다. Sentinel을 통해 자동으로 **Failover**가 발생할 수 있습니다.

#### 장점:
- **자동 Failover**: Master 노드 장애 시, **Sentinel**이 자동으로 **Slave 노드**를 승격하여 서비스 중단을 방지합니다.
- **모니터링 기능**: Sentinel이 Master와 Slave 노드를 지속적으로 모니터링합니다.

#### 단점:
- **구성 복잡성**: Sentinel 노드를 추가로 구성해야 하므로 설정이 복잡합니다.
- **성능 저하 가능성**: 여러 노드를 모니터링하고 Failover를 처리하기 위한 추가적인 리소스가 필요합니다.

---

### 4. **Redis 클러스터 구성**

**Redis Cluster**는 **수평적 확장성**을 제공하는 고가용성 구성 방식입니다. 여러 마스터 노드와 각 마스터에 대응하는 슬레이브 노드로 구성됩니다.

#### 장점:
- **수평 확장성**: 데이터를 여러 마스터 노드로 분산 저장하여 **쓰기 및 읽기 성능**을 확장할 수 있습니다.
- **자동 Failover**: 마스터 노드가 장애를 일으키면, 대응하는 슬레이브 노드가 자동으로 승격됩니다.
- **데이터 샤딩**: 데이터를 **샤드**로 분할하여 여러 마스터에 저장하므로 **데이터 분산 처리**가 가능합니다.

#### 단점:
- **구성 복잡성**: 클러스터 모드의 설정이 복잡하며, 노드 간의 통신을 위한 추가적인 포트 및 설정이 필요합니다.
- **데이터 일관성 문제**: 네트워크 파티션 또는 기타 문제로 인해 일시적으로 데이터 일관성 문제가 발생할 수 있습니다.

---

## 4. 결론

현재 제공된 **StatefulSet을 기반으로 한 Redis 클러스터 구성**은 고가용성과 데이터 영속성을 보장합니다. **Redis 클러스터 모드**를 통해 **수평 확장성**을 제공하며, 노드 간 통신 및 데이터 분산을 통해 높은 성능을 유지할 수 있습니다. **Headless Service**와 **Persistent Volume**을 통해 각 파드가 고유한 데이터를 저장하고, 클러스터 내에서 독립적으로 동작하도록 설계되었습니다.

Redis의 다양한 구성 방식은 프로젝트 요구 사항에 따라 선택될 수 있으며, 고가용성 및 성능을 고려한 최적의 구성을 선택하는 것이 중요합니다.

---


