## test.yml pod를 실행하여 kafka 클러스터가 외부파드들과 통신이 가능한지 확인

# kafka 사용법

1. 카프카 pod 접속

kubectl exec -it (카프카 pod name) -- /bin/bash

2. 토픽 생성

/opt/kafka/bin/kafka-topics.sh --create --topic <토픽이름> --bootstrap-server localhost:9092 --replication-factor 3 --partitions 1 복제랑 파티션은 원하는만큼

3. 토픽 목록확인

/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

4. 클라이언트와 연결

서비스 이름은 kafka-1, kafka-2, kafka-3 중 택 1

advertised listener가 9092로 되어있음

kafka-1:9092 이런식으로 연결하면 됨.