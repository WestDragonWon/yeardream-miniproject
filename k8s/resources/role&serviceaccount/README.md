# Kubernetes ServiceAccount & ClusterRole

Kubernetes에서 **ServiceAccount**와 **ClusterRole**은 클러스터 내에서 보안과 권한 관리를 위해 사용되는 중요한 개념입니다. 이 두 가지 객체는 파드가 클러스터 자원에 안전하게 접근할 수 있도록 하고, 필요한 권한만 부여하는 역할을 합니다. 이 문서에서는 ServiceAccount와 ClusterRole에 대해 설명하고, 그 관계를 설명합니다.

## 1. ServiceAccount란?

**ServiceAccount**는 파드가 Kubernetes API에 액세스할 때 사용할 수 있는 계정입니다. ServiceAccount는 사용자 계정과 다르게, 파드나 컨테이너 같은 애플리케이션 컴포넌트가 클러스터 내에서 동작하면서 특정 권한을 가지도록 하기 위해 사용됩니다. 기본적으로 파드가 생성될 때 ServiceAccount가 지정되지 않으면, "default" ServiceAccount가 할당됩니다.

- **ServiceAccount의 역할**: 파드가 클러스터 자원에 접근할 때 인증에 사용됩니다.
- **ServiceAccount의 사용 사례**: 파드가 특정 권한을 필요로 하여 API 리소스에 접근하거나 특정 작업을 수행해야 할 때 사용됩니다.

## 2. ClusterRole이란?

**ClusterRole**은 클러스터 내에서 API 리소스에 대한 권한을 정의하는 객체입니다. ClusterRole은 클러스터 전역에서 동작하며, 네임스페이스에 상관없이 모든 리소스에 대해 접근 권한을 설정할 수 있습니다. ClusterRole은 사용자가 직접 생성하거나 기본적으로 제공되는 ClusterRole을 사용할 수도 있습니다.

- **ClusterRole의 역할**: 파드, 서비스 계정, 또는 사용자에게 특정 작업(예: 읽기, 쓰기, 삭제 등)을 수행할 권한을 부여합니다.
- **ClusterRole의 사용 사례**: 여러 네임스페이스에서 공통된 권한이 필요한 경우, 네임스페이스와 무관하게 특정 리소스에 대한 접근을 관리할 때 사용됩니다.

## 3. ClusterRoleBinding이란?

**ClusterRoleBinding**은 **ClusterRole**과 **ServiceAccount** 또는 사용자(Subjects)를 연결하는 객체입니다. ClusterRoleBinding을 통해 특정 ServiceAccount에 ClusterRole의 권한을 할당하여, 해당 계정이 클러스터 전역에서 권한을 사용할 수 있도록 합니다.

- **ClusterRoleBinding의 역할**: ServiceAccount 또는 사용자가 특정 ClusterRole에 정의된 권한을 사용할 수 있도록 연결합니다.
- **ClusterRoleBinding의 사용 사례**: 여러 네임스페이스에서 동일한 권한을 사용하는 ServiceAccount를 관리할 때 사용됩니다.

## 4. ServiceAccount와 ClusterRole의 관계

Kubernetes에서는 파드가 특정 리소스에 접근할 때 ServiceAccount를 사용합니다. 하지만 ServiceAccount 자체는 권한을 가지지 않으며, **ClusterRole**과의 연동을 통해서만 권한을 부여받습니다. ClusterRole에 필요한 권한을 정의하고, ClusterRoleBinding을 사용해 ServiceAccount에 해당 권한을 부여합니다.

이와 같은 방식으로 파드는 ServiceAccount에 연결된 권한을 이용해 안전하게 Kubernetes API 리소스에 접근하거나 조작할 수 있습니다.

## 5. 사용 예시

### Airflow 서비스에 대한 예시

- **Airflow 서비스 계정**: Airflow가 동작하는 파드가 클러스터 내의 파드 리소스에 접근할 수 있도록 하기 위해 ServiceAccount를 생성하고, 필요한 권한을 부여합니다.
- **Airflow ClusterRole**: 파드 생성, 업데이트, 삭제 등 파드와 관련된 작업을 수행할 수 있도록 필요한 권한을 정의합니다.
- **Airflow ClusterRoleBinding**: Airflow 서비스 계정과 ClusterRole을 연결하여, 해당 서비스 계정이 파드 관련 작업을 수행할 수 있도록 설정합니다.

### Spark 서비스에 대한 예시

- **Spark 서비스 계정**: Spark 클러스터에서 동작하는 파드들이 서비스, 배치 작업, PVC, ConfigMap 등에 접근할 수 있도록 하는 ServiceAccount를 생성합니다.
- **Spark ClusterRole**: Spark 클러스터가 파드, PVC, ConfigMap, 배치 작업 등의 리소스를 생성하고 관리할 수 있도록 권한을 정의합니다.
- **Spark ClusterRoleBinding**: Spark 서비스 계정에 Spark 관련 권한을 부여하여, 해당 서비스 계정이 Spark 작업에 필요한 자원들에 접근할 수 있도록 설정합니다.

## 6. 주요 개념 요약

- **ServiceAccount**: 파드가 클러스터 내에서 동작하면서 사용할 수 있는 인증 계정.
- **ClusterRole**: 클러스터 전역에서 리소스에 대한 접근 권한을 정의하는 객체.
- **ClusterRoleBinding**: ClusterRole과 ServiceAccount를 연결하여 권한을 부여하는 객체.

이와 같이 Kubernetes에서는 보안과 접근 권한 관리를 위해 ServiceAccount, ClusterRole, 그리고 ClusterRoleBinding을 활용하여 파드의 권한을 세밀하게 제어할 수 있습니다.


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
```

## 쿠버네티스용 Spark 서비스 어카운트 및 역할 바인딩 설정

Kubernetes 클러스터에서 Spark를 실행할 때 필요한 `ServiceAccount`와 `RoleBinding`을 설정하는 구성 파일을 제공합니다. `ServiceAccount`는 Spark가 Kubernetes API와 상호작용하는 데 사용되며, `RoleBinding`을 통해 클러스터 리소스를 관리할 수 있는 권한을 부여합니다.
