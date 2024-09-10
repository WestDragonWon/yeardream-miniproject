
발생했던 오류 :
crd 안 만들면 오류 발생 -- CRD에 대해 찾아봄
Role 권한 문제 -> Role, ClusterRole, Binding에 대해 찾아봄

진행하며 새로 알게된 점 :
Deploy와 DaemonSet 차이에 대해 찾아봄

CRD등 알아야 하는게 너무 많아 처음부터 매니페스트 형식으로 구현하는 데 어려움을 겪음 -> helm 사용하는 방법으로 



metalLB를 정상적으로 사용하기위해서는 ARP 충돌을 방지해야 한다. 

(ARP는 IP를 네트워크에 광고하는 역할)

이 때, ARP 충돌을 방지하고, 노드 간에 IP를 올바르게 공유하기 위해 strictARP를 설정해줘야 한다.

(strictARP가 false인 경우 여러 노드가 동일한 IP 주소를 광고하고, true인 경우 해당 IP를 소유한 노드에서만 ARP 응답이 허용된다.)



strictARP 속성은 이용중인 프록시에 configmap 형식으로 등록이 되어있으며, configmap을 수정하는 방법으로는 kubectl edit 명령어로 직접 수정하는 방식과 .env파일을 통해 수정하는 방법이 있다.
(kubectl edit configmap kube-proxy -n kube-system)

resource가 부족한 4번 서버에서는 metallb가 정상적으로 동작하지 않음. 라벨을 만들어서 서버1, 2, 3에만 띄우는 방식으로  해결 (서버 1, 2, 3에는 main=y로, 서버4에는 main=n로 설정)


helm으로 인스톨하는 경우 CRD로 만들어지는 리소스를 바로 적용하는 방법을 찾지 못했음 ->  인스톨 후 apply하는 방식 사용 

