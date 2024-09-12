# 몽고디비
- Document 지향 NoSQL 데이터베이스로 JSON형식의 직렬화 형태인 BSON을 사용하여 속도증가와 RPC(원격 프로시저 호출)이 용이함
> 원격 프로시저 호출: 다른 시스템의 포로시저(함수)를 호출할 수 있게 해주는 프로토콜, 분산 시스템에서 시스템 간의 상호 작용을 위해 자주 사용됨.

---

- cluster 구성 이슈
mongodb는 클러스터를 레플리카셋으로 제공? https://www.mongodb.com/resources/products/compatibilities/deploying-a-mongodb-cluster-with-docker
레플리카셋과 클러스터를 혼용하여 사용함(개인적인 이해 이슈일 수 있음)
docker image도 community와 enterprise로 나뉘고, 클라우드 서비스를 유료로 제공

- Docker image를 이용한 k8s replica
pod간 연결을 위한 서비스 mongodb-svc.yaml
pv, pvc, statefulset 설정 mongodb-statefulset.yaml
pod안 mongodb에 명령어를 전달하기 위한 mongodb-cronjob.yaml

- 파드안 몽고디비에 명령어 전달 자동화를 위한 시도

-- initContainers option
pod생성후 mongodb가 띄워진 상태에서 커맨드를 보내야 되는데 파드 생성단계에서 커맨드를 보내니 오류가 발생함
파드가 init 상태에 걸려있는 오류 확인

-- lifecycle.postStart option
mongodb가 띄워지는 시간을 주기 위해 sleep을 걸면 pod에 sleep이 걸림

-- k8s cronjob
스케줄링을 통해 해결되는 듯 했으나 12일자 cronjob이 먼저돌고 pod가 생성되면 pod에 문제가 생기는 것을 확인, 수정중
mongodb-0이 커맨드를 받는 pod인데 crashloopback 상태에 빠짐
