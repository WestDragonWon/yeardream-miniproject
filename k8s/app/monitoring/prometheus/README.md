# prometheus

## 목차

1. 개요
2. 코드 설정
3. 사용법


### 개요

Prometheus는 시계열 데이터 수집 및 모니터링을 위한 오픈 소스 시스템으로, 강력한 쿼리 언어와 자동 서비스 탐지 기능을 제공한다. 다양한 메트릭을 실시간으로 분석하고 경고를 설정할 수 있어서 클라우드 환경에 적합하다.



### 코드 설정

	spec:
		nodeSelector:
			type: worker  # worker 노드에만 배포
		containers:
		- name: prometheus
			image: prom/prometheus:latest
			args:
			- "--config.file=/etc/prometheus/prometheus.yml"  # ConfigMap에서 설정 파일을 사용
			- "--storage.tsdb.path=/prometheus"  # 메트릭 데이터 저장 경로
			ports:
			- containerPort: 9090  # Prometheus 기본 포트
			volumeMounts:
			- name: prometheus-storage
			mountPath: /prometheus  # 기본 메트릭 저장 경로
			- name: prometheus-config  # ConfigMap을 마운트
			mountPath: /etc/prometheus
		volumes:
		- name: prometheus-storage
			persistentVolumeClaim:
			claimName: prometheus-pvc  # PVC를 통해 EFS 볼륨에 연결
		- name: prometheus-config  # ConfigMap 정의
			configMap:
			name: prometheus-config

**유의해서 봐야할 부분**

- args: 아래에 configmap에서 설정 파일을 사용하게 설정. 아래 경로는 prometheus의 주요 구성 파일이다.

또한 매트릭 저장 경로를 지정한다. 이 경로는 pv에 마운트 됨


### 사용법

1. 지정한 node port인 30111로 접근. <ec2_public_ip>:30111

2. 

![alt text](<이미지 25.png>)

표시된 버튼을 클릭하면 

![alt text](<이미지 26.png>)

사용 가능한 매트릭 열람이 가능하다.