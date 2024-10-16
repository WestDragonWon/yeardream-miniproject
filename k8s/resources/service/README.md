# Kubernetes Service

Kubernetes에서 **Service**는 클러스터 내에서 여러 파드(Pod)들에 대한 네트워크 액세스를 안정적으로 제공하는 추상화 객체입니다. 파드는 기본적으로 짧은 수명을 가지고 동적으로 생성되거나 제거되므로, 각 파드의 IP 주소가 변경될 수 있습니다. 이러한 이유로, 클러스터 내에서 안정적인 네트워크 통신을 위해 서비스가 필요합니다.

Kubernetes 서비스는 특정 파드 그룹(레이블 셀렉터로 정의됨)에 대한 접근을 제공하며, 이러한 파드들에 트래픽을 자동으로 로드 밸런싱합니다.

## 1. 서비스의 개념

Kubernetes에서 서비스는 동적으로 변화하는 파드의 IP 주소와 관계없이 클러스터 내 또는 외부에서 안정적인 네트워크 연결을 제공하기 위한 객체입니다. 서비스는 특정 레이블 셀렉터를 기반으로 해당 레이블을 가진 파드들에 요청을 전달합니다.

### 서비스의 역할

- 파드 간의 안정적인 네트워크 통신 보장
- 파드의 수명 주기와 관계없이 트래픽을 라우팅
- 로드 밸런싱을 통한 다수의 파드에 트래픽 분배
- 클러스터 외부에서 클러스터 내부의 파드에 접근할 수 있는 인터페이스 제공

## 2. 서비스의 기본 구성 요소

### 선택자(Selector)
서비스가 트래픽을 전달할 대상 파드를 결정하는 데 사용되는 레이블 셀렉터입니다. 선택자는 파드에 설정된 레이블과 매칭되는 파드들에게 트래픽을 라우팅합니다.

### 엔드포인트(Endpoints)
서비스와 연결된 실제 파드의 IP 주소와 포트 정보를 포함하는 목록입니다. 서비스는 엔드포인트를 통해 트래픽을 대상 파드로 전달합니다.

### 클러스터 IP(Cluster IP)
기본적으로 각 서비스는 클러스터 내에서 유일한 가상 IP 주소(클러스터 IP)를 할당받습니다. 이 IP 주소를 통해 파드와 서비스 간 통신이 이루어집니다.

### 포트(Ports)
서비스가 외부 요청을 받는 포트입니다. 각 포트는 해당 파드로 전달될 때 사용할 포트로 매핑됩니다.

## 3. 서비스의 유형

Kubernetes에서는 서비스의 유형에 따라 트래픽을 처리하는 방식이 다릅니다. 주요 서비스 유형은 다음과 같습니다.

### 3.1 ClusterIP
- **기본 서비스 유형**으로, 클러스터 내에서만 접근 가능한 내부 IP를 할당합니다.
- 클러스터 외부에서는 접근할 수 없으며, 클러스터 내부에서 파드들이 서로 통신할 때 주로 사용됩니다.

### 3.2 NodePort
- 서비스가 클러스터 외부에서 접근 가능하도록 각 노드의 고정된 포트 번호를 할당합니다.
- 외부 트래픽이 지정된 노드 포트를 통해 들어와 해당 서비스의 대상 파드로 전달됩니다.

### 3.3 LoadBalancer
- **클라우드 환경**에서 주로 사용되며, 외부 로드 밸런서를 통해 서비스를 외부에 노출합니다.
- 클라우드 제공자(AWS, GCP, Azure 등)에 따라 외부 IP 주소를 자동으로 할당받고, 로드 밸런서를 통해 트래픽을 해당 서비스의 파드로 라우팅합니다.

### 3.4 ExternalName
- 외부 DNS 이름을 서비스로 맵핑합니다.
- 클러스터 외부의 서비스나 도메인 이름으로 트래픽을 전달할 때 사용됩니다.

## 4. Kubernetes 서비스 로드 밸런싱

Kubernetes 서비스는 여러 파드에 대한 로드 밸런싱을 제공합니다. `ClusterIP` 서비스를 이용하면, 요청은 여러 파드에 분산되어 처리됩니다. 이때 파드 간의 로드 밸런싱은 **쿠버네티스 kube-proxy**를 통해 이루어집니다.

쿠버네티스는 iptables 또는 IPVS를 사용하여 각 노드에서 서비스에 연결된 파드들로의 트래픽을 라우팅하고 로드 밸런싱을 수행합니다.

## 5. Headless 서비스

일반 서비스와 달리, **헤드리스(Headless) 서비스**는 클러스터 IP를 생성하지 않고, 파드에 직접 연결할 수 있는 방법을 제공합니다. StatefulSet에서 주로 사용되며, 파드의 개별 IP 주소를 얻거나, 특정 파드에 직접 연결하고자 할 때 유용합니다.

## 6. 서비스 디스커버리

Kubernetes는 **DNS**를 사용해 서비스 디스커버리를 제공합니다. 클러스터 내에서 서비스는 자동으로 DNS 이름을 통해 접근할 수 있으며, 기본적으로 서비스 이름과 네임스페이스에 따라 DNS 이름이 할당됩니다.

- **서비스 DNS 이름 형식**: `service-name.namespace.svc.cluster.local`
  - 예: `my-service.default.svc.cluster.local`

## 7. 서비스와 엔드포인트 관계

서비스가 트래픽을 라우팅할 대상 파드는 엔드포인트 객체로 관리됩니다. 엔드포인트는 서비스와 선택자(Selector)를 기반으로 매핑된 파드들의 IP 주소와 포트를 저장하는 객체입니다. 즉, 서비스는 엔드포인트를 통해 해당 파드들로 트래픽을 전달합니다.
