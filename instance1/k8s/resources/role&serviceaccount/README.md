# ServiceAccount

## 쿠버네티스용 Spark 서비스 어카운트 및 역할 바인딩 설정

이 저장소는 Kubernetes 클러스터에서 Spark를 실행할 때 필요한 `ServiceAccount`와 `RoleBinding`을 설정하는 구성 파일을 제공합니다. `ServiceAccount`는 Spark가 Kubernetes API와 상호작용하는 데 사용되며, `RoleBinding`을 통해 클러스터 리소스를 관리할 수 있는 권한을 부여합니다.

## 개요

쿠버네티스에서 `ServiceAccount`는 파드 내에서 실행되는 프로세스가 사용할 수 있는 신원 정보입니다. 이 구성 파일은 `spark`라는 이름의 서비스 어카운트를 `spark` 네임스페이스에 생성하고, `ClusterRole`인 `edit` 권한을 서비스 어카운트에 바인딩하여 쿠버네티스 리소스를 생성, 수정, 삭제할 수 있도록 설정합니다.

## 파일 설명

### `service-account.yaml`

이 YAML 파일은 두 가지 섹션으로 나누어집니다:
1. **ServiceAccount**: `spark` 네임스페이스에 `spark`라는 이름의 서비스 어카운트를 정의합니다.
2. **RoleBinding**: `spark` 서비스 어카운트를 `edit` 권한을 가진 `ClusterRole`에 바인딩하여, 리소스를 관리할 수 있도록 설정합니다.

### 서비스 어카운트 정의

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: spark
  namespace: spark
