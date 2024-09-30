# kafka


## 목차

1. [개요](#개요)
2. [실행환경](#실행환경)
3. [코드 설명](#코드-설명)
4. [사용법](#사용법)
5. [트러블슈팅]()

### 개요

카프카는 높은 성능, 내구성, 확장성, 실시간 데이터 처리 능력 등 다양한 이점을 제공하여, 데이터 파이프라인과 스트리밍 애플리케이션에 사용되고 있음.

### 실행환경

- 클러스터 환경:
  - 쿠버네티스 버전: v1.28.13
  - 카프카 버전: Apache Kafka 3.7.1

### 코드 설명


	apiVersion: apps/v1
	kind: Deployment
	metadata:
	name: kafka-1
	spec:
	replicas: 1
	selector:
		matchLabels:
		app: kafka
		instance: kafka-1

- apiVersion: 이 리소스의 API 버전을 명시하는 부분
- kind: 리소스 종류 지정. 여기서는 Deployment를 사용
- metadata: Deployment의 이름을 kafka-1로 설정
- spec: deployment의 구체적인 설정
- replicas: 1 파드 복제본 수

**Deployment**

상태 관리: 파드가 실패하면 자동으로 재시작하거나 새로운 파드를 생성하여 원하는 상태를 유지함.

롤링 업데이트: 애플리케이션의 새 버전을 배포할 때, 기존 버전을 점진적으로 교체할 수 있음. 그리하여 다운타임 없이 업데이트를 수행이 가능함.

롤백 기능: 문제가 발생했을 때 이전 버전으로 쉽게 되돌릴 수 있는 기능을 제공.

스케일링: 어플리케이션의 필요에 따라 파드의 복제본 수를 쉽게 조정할 수 있음. 트래픽이 많을 때 복제본 수를 늘리고, 적을 때 줄일 수 있다.

노드 선택성: 특정 노드에 파드를 배포하도록 설정할 수 있음.


#### 특정 노드에서만 배포되도록 하는 설정

template 밑에 설정하면 됨.

	spec:
		affinity:
			nodeAffinity:
			requiredDuringSchedulingIgnoredDuringExecution:
				nodeSelectorTerms:
				- matchExpressions:
				- key: kubernetes.io/hostname
					operator: In
					values:
					- worker1

pod의 구체적인 설정을 하는 부분. 

- affinity를 통해 특정 노드에 배포되도록 설정
- nodeAffinity를 통해 특정 노드에 대한 선호도 설정
- requiredDuringSchedulingIgnoredDuringExecution 스케줄링 시의 필수조건을 정의. 조건을 만족하지 않으면 실행되지 않으면 노드에 배포하지 않음
- nodeSelectorTerms 노드 선택 기준 정의 
- matchExpressions 특정 키에 대한 조건
- key 조건을 적용할 노드의 레이블 키
- operator: In 조건의 유형. values에 지정된 값 중에서 일치해야함
- values 키에 허용되는 값. 



		containers:
		- name: kafka
		image: apache/kafka:3.7.1
		ports:
		- containerPort: 9092
		- containerPort: 9093

- containers: pod에 포함될 컨테이너 리스트
- name: 컨테이너 이름
- image: 사용할 도커 이미지
- ports: 각각 컨테이너 포트 번호. 9092(브로커), 9093(컨트롤러)

		env:
        - name: KAFKA_PROCESS_ROLES
          value: "broker,controller"
        - name: KAFKA_NODE_ID
          value: "1"
        - name: KAFKA_CONTROLLER_QUORUM_VOTERS
          value: "1@kafka-1:9093,2@kafka-2:9093,3@kafka-3:9093"

- env: 컨테이너 환경변수 설정
- name: 환경변수 이름
- value: 환경변수 값. broker와 controller 두 개의 역할을 다 하는데 **kraft 모드에서만 가능**
- KAFKA_NODE_ID 각 브로커의 고유 ID
- KAFKA_CONTROLLER_QUORUM_VOTERS 컨트롤러 투표자 목록. 모든 kafka 브로커의 서비스가 포함되어야함

		- name: KAFKA_LISTENERS
          value: "PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093"
        - name: KAFKA_ADVERTISED_LISTENERS
          value: "PLAINTEXT://kafka-1:9092"

- KAFKA_LISTENERS 브로커가 수신할 프로토콜과 포트 설정. 여기선 PLAINTEXT를 사용
- KAFKA_ADVERTISED_LISTENERS 클라이언트가 이 브로커에 연결할 때 사용하는 주소

		- name: KAFKA_LOG_DIRS
          value: "/var/lib/kafka/data"
        - name: KAFKA_LISTENER_SECURITY_PROTOCOL_MAP
          value: "PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT"
        - name: KAFKA_INTER_BROKER_LISTENER_NAME
          value: "PLAINTEXT"
        - name: KAFKA_AUTO_CREATE_TOPICS_ENABLE
          value: "false"
        - name: KAFKA_CONTROLLER_LISTENER_NAMES
          value: "CONTROLLER"

- KAFKA_LOG_DIRS 로그 파일이 저장되는 디렉토리
- KAFKA_LISTENER_SECURITY_PROTOCOL_MAP 각 리스너의 보안 프로토콜
- KAFKA_INTER_BROKER_LISTENER_NAM 브로커 간 통신에 사용할 리스너 이름
- KAFKA_AUTO_CREATE_TOPICS_ENABLE 자동 토픽 생성여부. 자동 생성했을 때 생겼던 이슈 때문에 false로 설정
- KAFKA_CONTROLLER_LISTENER_NAMES 컨트롤러가 사용할 리스너 이름


#### 현업에서 사용되는 설정

		- name: KAFKA_LOG_RETENTION_MS
          value: "604800000"
        - name: KAFKA_MESSAGE_MAX_BYTES
          value: "10485760"  
        - name: KAFKA_REPLICA_FETCH_MAX_BYTES
          value: "10485760"  
        - name: KAFKA_MAX_PARTITION_FETCH_BYTES
          value: "10485760"

- KAFKA_LOG_RETENTION_MS 로그 보존기간을 밀리초 단위로 설정. 보통 7일 정도 유지한다고 함
- KAFKA_MESSAGE_MAX_BYTES 각 메세지의 최대 크기를 바이트 단위로 설정. 지금은 10MB로 되어 있으나 이 이상으로 설정하면 성능에 문제가 생길 수 있음. default는 1MB
- KAFKA_REPLICA_FETCH_MAX_BYTES, KAFKA_MAX_PARTITION_FETCH_BYTES 마찬가지로 복제본과 각 파티션이 가져올 수 있는 최대 바이트도 10MB로 설정함

		volumes:
			- name: kafka-storage
				persistentVolumeClaim:
					claimName: kafka-pvc-1

- volumes: 파드에서 사용할 볼륨 정의 부분
- persistentVolumeClaim: 외부 저장소와 연결하는 부분

#### Service

	apiVersion: v1
	kind: Service
	metadata:
	name: kafka-1

- kind 리소스 종류는 Service

		spec:
			ports:
			- name: plaintext
				port: 9092
				targetPort: 9092
				protocol: TCP
			- name: controller
				port: 9093
				targetPort: 9093
				protocol: TCP

- 포트 설정: 두 개의 포트를 정의함. 9092(Plaintext)는 일반 클라이언트와의 통신을 위한 포트. 9093 (controller)는 카프카의 컨트롤러 역할을 위한 포트

		selector:
			app: kafka
			instance: kafka-1

- 이 서비스는 app: kafka, instance: kafka-1 레이블을 가진 파드에 요청을 전달함. 특정 카프카 브로커와 연결되도록 설정

### 사용법

1. kafka pod 접속

		kubectl exec -it <kafka pod name> -- /bin/bash

2. 아래 경로로 이동

		cd /opt/kafka/bin

3. 토픽 생성

		./kafka-topics.sh --create --topic my-topic --bootstrap-server kafka-1:9092 --partitions 1 --replication-factor 3

4. 프로듀서 설정

주제에 메세지를 보내기 위해 프로듀서 설정.

		./kafka-console-producer.sh --topic my-topic --bootstrap-server kafka-1:9092

입력 후 메세지를 입력하고 엔터를 누르면 해당 토픽으로 메시지가 전송됨.

5. 컨슈머 설정

		./kafka-console-consumer.sh --topic my-topic --from-beginning --bootstrap-server kafka-1:9092

my-topic에서 모든 메시지를 처음부터 읽어옴.

6. 토픽 목록

		./kafka-topics.sh --list --bootstrap-server kafka-1:9092


7. 같은 클러스터 내부 클라이언트와 연결

	서비스 이름은 kafka-1, kafka-2, kafka-3 중 택 1

	advertised listener가 9092로 되어있음.

	kafka-1:9092 이런식으로 연결

### 트러블슈팅

1. 필수적인 요소들

	- kraft 모드를 사용중이기 때문에 생긴 이슈
				
			- name: KAFKA_PROCESS_ROLES
			value: "broker,controller"
		
		주키퍼와는 달리 kraft 모드에선 브로커 컨트롤러가 동일한 인스턴스에서 실행될 수 있게 함.

			- name: KAFKA_ADVERTISED_LISTENERS
          	value: "PLAINTEXT://kafka-1:9092"

		주키퍼에선 value에 controller도 들어가지만 kraft에선 controller 내용이 들어가면 오류가 생김.

2. DNS?

	쿠버네티스에선 서비스 이름으로 DNS 연결이 가능하기 때문에 service에서 설정한 이름으로 클라이언트와 연결 해야함.