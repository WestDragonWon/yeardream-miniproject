## Pod를 만들어서 테스트하는 이유
- kafka service가 clusterIp로 구성되어 있어 파드간 통신은 가능하지만 k8s 클러스터 외부, 인스턴스 상에서는 통신이 불가능함
## dockerfile 설명
- test pod이므로 python slim 이미지를 사용했고 --no-cache-dir 옵션을 통해 사이즈를 줄임.
- Pod에서 k8s 클러스터 외부 경로인 인스턴스 파일에 접근 시 문제 해결을 위해 데이터를 도커이미지에 같이 복사
- Pod생성후 자동으로 python 실행
## ConfluentKafkaProducer.py
- 원하는 chunk 사이즈로 데이터를 읽어 confluent kafka 라이브러리의 Producer로 kafka에 넣음
> kafka message의 기본 사이즈가 1mb인걸 고려해서 데이터를 분해하여 넣는 것이 처리속도 상 중요하다고 생각했으나, 데이터를 분해하는 작업(pd 특정구간 읽기), 이후 여러번의 produce airflow dag 작업이 더 시간이 많이 들었음.
