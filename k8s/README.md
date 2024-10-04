# `K8s` 디렉토리에는 Kubernetes 와 관련된 모든 리소스가 포함됩니다.
## 
   - [app]
     - [datacollection]
     - [db]
       - [elasticsearch]
       - [mongodb](./app/db/mongodb/README.md)
       - [postgresql](./app/db/postgresql/README.md)
       - [redis](./app/db/redis/README.md)
     - [monitoring]
       - [alertmanager](./app/monitoring/alertmanager/README.md)
       - [exporter]
       - [grafana]
       - [prometheus]
     - [processing]
       - [kafka](./app/processing/kafka/README.md)
       - [spark](./app/processing/spark/README.md)
     - [serving]
       - [FastAPI](./app/serving/README.md)
     - [systeam]
       - [aws-ebs-efs](./app/system/aws-ebs-efs/README.md)
       - [dashboard](./app/system/dashboard/README.md)
     - [workflow]
       - [airflow](./app/workflow/airflow/README.md)
       - [mlflow](./app/workflow/mlflow/README.md)
   - [resources](./resources/README.md)
     - [configmap](./resources/configmap/README.md)
     - [pv](./resources/pv/README.md)
     - [role&serviceaccount](./resources/role&serviceaccount/README.md)
     - [secret](./resources/secret/README.md)
     - [service](./resources/service/README.md)
     - [storageclass](./resources/storageclass/README.md)


# Pod가 특정 노드에 배치될 수 있도록 제어하는 방법
## NodeSelector를 이용한 라벨 기반 스케줄링

### 라벨링 된 노드 조회 방법
```bash
kubectl get nodes --show-labels
kubectl get nodes -l type=worker --show-labels
```

### 노드에 active=enabled 라는 라벨링 방법
```bash
kubectl label nodes ip-172-31-5-84 type=worker
```
### 키가 active 인 라벨 제거 방법
```bash
kubectl label nodes ip-172-31-5-84 type-
```
### 위 명령어로 라벨링후 적용할 yml 파일에 아래 내용 추가
```yml
spec:
  template:
    spec:
      nodeSelector:
        type: "worker"
```

## 라벨링 구성 정보

### key값 
- type
##  value
instance1
type: "master"

instance2
type: "worker"

instance3
type: "worker"

instance4 
type: "mlops"

instance5
type: "worker"


- 쉽고 간단한 설정 
- 단순한 매칭 조건
- 하지만 제약 조건 설정의 한계가 큼
- 예를 들어, 여러 개의 조건(예: 디스크 유형이 SSD이면서 리전이 us-west-1이어야 한다)을 동시에 적용해야 하는 경우에는 **노드 어피니티(Node Affinity)**를 사용하는 것이 더 적합합니다.


## Node Affinity

### 특정 하드웨어 요구사항:

고성능 워크로드는 특정 하드웨어(GPU, SSD 스토리지 등)를 요구할 수 있습니다. 노드 어피니티를 사용하여 이러한 하드웨어가 있는 노드에만 Pod를 배치할 수 있습니다.

### 리전/가용 영역 제어:

클러스터 내에서 네트워크 지연 시간을 줄이기 위해 특정 리전이나 가용 영역의 노드에만 워크로드를 배치하고자 할 때 사용할 수 있습니다.

### 테스트 환경 격리:

개발 또는 테스트 환경을 특정 노드에만 배치하여 프로덕션 환경과 격리된 상태에서 운영할 수 있습니다.

`requiredDuringSchedulingIgnoredDuringExecution`: 필수 어피니티 조건. 지정된 조건을 반드시 만족하는 노드에만 Pod가 스케줄링됩니다.
`preferredDuringSchedulingIgnoredDuringExecution`: 선호 어피니티 조건. 지정된 조건을 만족하는 노드에 스케줄링을 시도하지만, 필수는 아닙니다.

```yml
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: active  # 노드의 'active' 라벨을 사용
            operator: In # 지정된 값 목록 중 하나와 일치해야 합니다.
            values:
            - enabled # 'enabled' 값을 가진 노드에만 Pod를 스케줄링
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 1 # 조건의 우선순위를 나타내는 값입니다. 값이 높을수록 조건이 더 중요하게 고려됩니다.
        preference:
          matchExpressions:
          - key: zone
            operator: In
            values:
            - ap-northeast-2a  # 가능한 경우 'ap-northeast-2a' 리전에 있는 노드를 선호
```

### 노드 어피니티의 주요 연산자
- In: 지정된 값 목록 중 하나와 일치해야 합니다.
- NotIn: 지정된 값 목록 중 하나와 일치하지 않아야 합니다.
- Exists: 지정된 키가 노드에 존재해야 합니다.
- DoesNotExist: 지정된 키가 노드에 존재하지 않아야 합니다.
- Gt: 지정된 키의 값이 특정 값보다 커야 합니다.
- Lt: 지정된 키의 값이 특정 값보다 작아야 합니다.


---




