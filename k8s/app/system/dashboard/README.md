
## 설치
(https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/ 참고)
1. 레포지토리 등록
    helm repo add kubernetes-dashboard https://kubernetes.github.io/dashboard/
2. 인스톨
    helm upgrade --install dashboard kubernetes-dashboard/kubernetes-dashboard --create-namespace --namespace system

---
## 대시보드 UI 접근

클러스터 데이터를 보호하기 위해 RBAC 설정이 기본으로 구현되어있다.
-> 유저별 접근권한, 인증 必

우선 유저를 만들고, 쿠버네티스에 기본적으로 존재하는 cluster-admin 역할을 바인딩시켜 유저의 권한을 만든다.
그 다음, 해당 유저에 대한 토큰을 발급하여 dashboard에서 해당 유저를 인증할 수 있게 한다. (현재 대시보드는 토큰에 의한 인증만을 지원)

---
## 파일 목록 :

**.env** : 토큰이 저장될 파일, 깃 등 외부에 노출되면 안 될 것 같아  .env 형식 사용

**adminuser.yaml** : 대시보드에 접근 할 유저를 생성해야 함- cluster-admin은 쿠버네티스에서 가장 강력한 내장 ClusterRole (권한 범위 : 리소스 생성, 조회, 수정, 삭제 등 작업 수행 가능, 다른 네임스페이스의 리소스에 대해서도 동일한 권한을 가지므로 보안 리스크가 있다.)

**port-forward.log** : 포트포워딩 방식으로 돌아갈 대시보드의 접근 기록 등 로그

**secret.yaml** : admin-user가 대시보드에 접속하기 위해서는 토큰이 필요한데, 이 토큰을 발급받는 방식으로 secret을 사용했다.  Secret의 타입을 kubernetes.io/service-account-token로 주면 서비스 어카운트와 연결된 토큰을 발급할 수 있다.

**start-dashboard.sh** : 포트포워딩과 토큰을 발급하고, 출력하는 쉘 스크립트
포트 포워딩은 nohup으로

---

토큰 발급 방법은 두 가지가 존재
1. kubectl 명령어를 이용해 짧은 유효기간을 갖는 토큰 발급 (유효기간 1시간정도, 정확하지는 않음)
    kubectl -n kubernetes-dashboard create token admin-user 명령어로 admin-user에 대한 토큰을 발급
    
2. Secret을 이용한  유저에 바운드되는 토큰 발급 (유효기간 없음, 마찬가지로 정확하지 않다)
    현재 구현한 방법

---

https로만 동작하며, http접속이 안되는 문제가 있다. > 보안적인 문제가 있어서 이렇게 설계된 것으로 추정

대시보드에 접속하려면 토큰이 필요하고, 토큰은 시크릿을 등록하는 방법으로 발급받는다. 