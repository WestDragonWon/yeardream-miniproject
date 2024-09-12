
## metalLB의 역할

우선 AWS, GCP 등 여러 클라우드에서 제공하는 서비스 중 하나인 **LoadBalancer**는 클라우드 상에서 구현한 서비스에 고정 IP를 할당하여 외부 사용자에 대한 접근을 가능하게 하고, 외부 트래픽을 내부의 여러 노드에 자동으로 분배하여 부하를 분산하는 역할을 한다.

metalLB는 로드밸런서와 유사한 기능을 제공하는 **로드밸런서 구현체**이며, 마찬가지로 구현한 서비스에 고정 IP를 할당하고, 트래픽을 분산하는 역할을 할 수 있다.

Amazon 클라우드로 서비스를 구현중인 현재 프로젝트에서, 유료로 제공중인 LoadBalancer의 비용을 절감하고, 서비스들을 직접 제어하여 유연성을 주기위해 metalLB를 사용하였다.

---
## 환경 구성

ARP 충돌을 방지하고, 노드 간에 IP를 올바르게 공유하기 위해 **strictARP**를 설정해줘야 한다.
(ARP : IP 주소를 MAC 주소로 변환하는 프로토콜)

MetalLB는 클러스터로 구성된 노드들에서 VIP(Virtual IP)를 통해 외부의 트래픽을 수신한다.
따라서 요청에 대한 응답 또한 여러 노드가 할 수 있으며, 이를 방지하고 각 노드가 소유한 VIP에 대해서만 ARP요청을 응답하게 해주는 strictARP 설정을 해주어야 한다.

strictARP 속성은 이용중인 프록시에 configmap 형식으로 등록이 되어있으며,  kubectl edit 명령어로 직접 수정하는 방식으로 설정하였다.

```
kubectl edit configmap kube-proxy -n kube-system
```
```
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: "ipvs"
ipvs:
  strictARP: true
```
---

## 설치
(https://metallb.universe.tf/installation/ 참고)

```
helm repo add metallb https://metallb.github.io/metallb

helm install metallb metallb/metallb
```

metalLB로 LoadBalancer 타입의 서비스에 직접 IP를 할당하기 위해 CRD로 정의된 IPAddressPool, L2Advertisement를 구현하였다.
```
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: my-metallb-config
  namespace: system
spec:
  addresses:
  - 172.31.41.221-172.31.41.231
  autoAssign: true
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: my-metallb-config
  namespace: system
spec:
  ipAddressPools:
    - my-metallb-config

```
이를 통해 각 서비스에 172.31.41.221-172.31.41.231로 정의한 IP가 할당되게 하였다.

---

구상 당시에는 도커 이미지를 사용한 manifest(helm을 사용하지 않고, yaml파일로 deployment, daemonset 등을 정의) 방식으로 구현하고 싶었지만, 서비스에 대한 정확한 이해가 필요하고, 이에 너무 많은 시간이 소비될 것으로 판단하여 helm을 사용하였다. 

manifest 방식으로 구현하면서 겪었던 어려움과 새로 알게된 점에 대해 작성하였다.

마주한 어려움 :
1. CRD에 대한 정확한 이해 필요.
    CRD란 사용자가 직접 정의하여 쿠버네티스의 기능을 확장할 수 있게 해주는 리소스이다.
    metalLB같은 복잡한 시스템은 자신만의 리소스가 필요한데, metalLB에서 정의된 CRD 중 프로젝트에서 반드시 필요한 CRD가 무엇인지 파악하고, 그것을 직접 구현하는데 어려움을 겪었다.
2. Role 권한 문제.
    metalLB는 RBAC를 사용하여 사용자들에 대한 접근을 제한하는데, metalLB에 필요한 역할이 무엇인지 파악하는데 어려움을 겪었다.

새로 알게된 점 :
DaemonSet 방식에 대해 공부하였다.
정해진 replica 개수만큼 Pod를 띄우는 Deployment방식, Pod의 상태가 중요하여 고유한 이름을 유지시켜주고, 순차적으로 생성 및 삭제하는 StatefulSet방식과 달리, **DaemonSet 방식은 원하는 노드에 Pod를 하나씩 배포**하기 때문에 로그를 수집하거나, 노드의 상태를 모니터링하기 쉽다.
metalLB Pod중 Speaker는 자신이 속한 노드의 IP 주소를 외부에 알려주는데, 특정 노드에 Speaker가 존재하지 않는다면 해당 노드의 VIP를 알 수 없게된다. 또한, node가 늘어나는 경우 자동으로 해당 node에 pod를 생성하여 확장성 측면에서도 유리하다.
node에 라벨링을 하는 방식으로 필요한 node에만 pod를 띄울 수 있다.


helm으로 인스톨하는 경우 CRD로 만들어지는 리소스를 바로 적용하는 방법을 찾지 못했음 ->  인스톨 후 apply하는 방식 사용 (현재 파일명은 value라고 되어있지만, config형식의 파일임)
