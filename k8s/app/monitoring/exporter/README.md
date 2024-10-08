# exporter

## 목차

1. 개요
2. 코드설명
3. 사용법
	- prometheus config
4. 유의사항
----

### 개요

Exporter는 Prometheus의 핵심 구성 요소로, 다양한 시스템의 메트릭을 수집하고 이를 Prometheus에 통합하여 모니터링 및 경고 시스템을 구축하는 데 중요한 역할을 함. 이를 통해 운영자는 시스템 성능을 실시간으로 감시하고, 문제를 조기에 발견하여 대응할 수 있다.

### 코드설명

**es-exporter**

	apiVersion: apps/v1
	kind: Deployment
	metadata:
	name: elasticsearch-exporter
	labels:
		app: elasticsearch-exporter
	spec:
	replicas: 1
	selector:
		matchLabels:
		app: elasticsearch-exporter
	template:
		metadata:
		labels:
			app: elasticsearch-exporter
		spec:
		containers:
		- name: elasticsearch-exporter
			image: prometheuscommunity/elasticsearch-exporter:latest
			args:
			- '--es.uri=http://elasticsearch:9200/'  # 서비스 이름
			ports:
			- containerPort: 9114  # 기본 포트
			env:
			- name: ES_USERNAME
			valueFrom:
				secretKeyRef:
				name: db
				key: ELASTICSEARCH_USERNAME
			- name: ES_PASSWORD 
			valueFrom:
				secretKeyRef:
				name: db
				key: ELASTICSEARCH_PASSWORD

	---
	apiVersion: v1
	kind: Service
	metadata:
	name: elasticsearch-exporter
	labels:
		app: elasticsearch-exporter
	spec:
	type: NodePort
	ports:
	- name: metrics
		port: 9114
		targetPort: 9114
		nodePort: 30333
	selector:
		app: elasticsearch-exporter

- 모든 exporter들은 args 설정이 가장 중요함. args 작성 방식이 다 다른데 각 이미지의 github 밑 docker hub에서 작성 방식을 찾아봐야한다. 다만 공식에서 설명하는 방법이 되지 않는 경우도 있는데 이 경우는 보편적으로 쓰는 방식이나 llm이나 구글링을 추천.

- 서비스에 node port 설정은 웹에서 매트릭이 잘 불러와졌는지, 혹은 연결이 잘 되었는지 확인하기 위해서이다. 보통 연결이 안됐을 때는 up이 들어간 매트릭 이름에서 0 또는 1로 상태를 표시해준다. 0은 연결 안됨, 1은 연결됨.

**kafka-exporter**

	spec:
		containers:
		- name: kafka-exporter
			image: danielqsj/kafka-exporter:latest
			args:
			- "--kafka.server=kafka-0:9092"  
			- "--kafka.server=kafka-1:9092"
			- "--kafka.server=kafka-2:9092" 
			ports:
			- containerPort: 9308

- 다른 설정은 동일하고 args에서 인자를 불러오는 부분만 주의하면 된다. 모든 브로커를 봐야하므로 모두 연결해준다.

**mongodb-exporter**

	spec:
		nodeSelector:
			type: worker  # worker 노드에 배포
		containers:
		- name: mongodb-exporter
			image: bitnami/mongodb-exporter:latest
			ports:
			- containerPort: 9216  # MongoDB Exporter 기본 포트
			env:
			- name: MONGODB_URI
			value: "mongodb://mongodb:27017/mongo?replicaSet=MainRepSet"  # MongoDB 연결 URI

- mongodb는 value 값의 uri 설정이 가장 중요함

**postgre-exporter**

	value: "user=$(POSTGRES_USER) password=$(POSTGRES_PASSWORD) host=postgres port=5432 dbname=s32db sslmode=disable"
			ports:
				- containerPort: 9187
			command: ["/bin/sh", "-c"]
			args:
				- |
				/postgres_exporter --web.listen-address=:9187 --web.telemetry-path=/metrics


- value와 command가 겹치는 것처럼 보이는 이유:
value에서 DSN을 설정하는 것과 command에서 Exporter를 실행하는 것은 서로 다른 목적. DSN은 데이터베이스 연결 정보를 제공하고, Exporter는 메트릭을 수집하고 노출하는 역할을 한다.

- 결론:
Exporter가 PostgreSQL 데이터베이스에 연결하고, 메트릭을 수집하기 위한 필수적인 정보와 실행 환경을 설정하는 것이다. 각 요소는 서로 보완적인 역할을 하며, PostgreSQL Exporter가 제대로 작동하기 위해 함께 필요함.

**redis**

	value: "redis-cluster:6379"

- redis 서비스 이름과 지정한 포트 이름만 vaule 값에 넣어주면 된다.


### 유의사항

**args에 인자값 넣는 방식**

이 부분에서 가장 많은 시행착오를 거쳤다. 각 이미지에 맞는 방식을 찾아야 한다.


### 사용법

#### prometheus config


		apiVersion: v1
		kind: ConfigMap
		metadata:
		name: prometheus-config
		data:
		prometheus.yml: |
			global:
			scrape_interval: 15s

			alerting:
			alertmanagers:
			- static_configs:
				- targets:
				- 'alertmanager:9093'
			
			scrape_configs:
			- job_name: 'prometheus'
				static_configs:
				- targets: ['localhost:9090']

			- job_name: 'postgres-exporter'  # PostgreSQL Exporter 추가
				static_configs:
				- targets: ['postgres-exporter:9187']  # PostgreSQL Exporter 서비스 이름과 포트

			- job_name: 'kafka-exporter'  # Kafka Exporter 추가
				static_configs:
				- targets: ['kafka-exporter:9308']  # Kafka Exporter 서비스 이름과 포트

			- job_name: 'redis-exporter'
				static_configs:
				- targets: ['redis-exporter:9121']

			- job_name: 'mongodb-exporter'  # MongoDB Exporter 추가
				static_configs:
				- targets: ['mongodb-exporter:9216']

			- job_name: 'elasticsearch-exporter'  # Elasticsearch Exporter 추가
				static_configs:
				- targets: ['elasticsearch-exporter:9114']

		alert.rules: |
			groups:
			- name: server-down-alert
				rules:
				- alert: PostgresDown
					expr: pg_up == 0
					for: 1m
					labels:
					severity: critical
					annotations:
					summary: "PostgreSQL instance is down"
					description: "PostgreSQL instance {{ $labels.instance }} is down."


위 코드는 prometheus의 confimap 설정파일이다.

job 이름을 지정해주고 앞서 정의했던 exporter들의 서비스 이름과 포트 이름을 지정해주면 된다.



### 유의사항

정상 작동한다면 up과 관련된 매트릭 정보에서 1이 뜰것이고 아니라면 0이 뜰 것이다.

![alt text](<이미지 41.png>)

postgres의 매트릭 정보를 웹에 띄운것인데 이처럼 pg_up 매트릭이 있고 1이 떠있는걸 볼 수 있다. 만약 0이 떠있다면 애플리케이션에 제대로 접근하지 못했다는 뜻이니 디버깅을 해보도록 하자.