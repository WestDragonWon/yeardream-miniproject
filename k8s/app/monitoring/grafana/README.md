# grafana

## 목차

1. 개요
2. 코드설정
3. 사용법

		apiVersion: v1
		kind: PersistentVolumeClaim
		metadata:
		name: grafana-efs-claim
		spec:
		accessModes:
			- ReadWriteMany
		resources:
			requests:
			storage: 1Gi  # 요청하는 스토리지 크기
		storageClassName: grafana-storageclass  # 사용 중인 StorageClass 이름

		---
		apiVersion: apps/v1
		kind: Deployment
		metadata:
		name: grafana
		spec:
		replicas: 1
		selector:
			matchLabels:
			app: grafana
		template:
			metadata:
			labels:
				app: grafana
			spec:
			containers:
				- name: grafana
				image: grafana/grafana:latest
				ports:
					- containerPort: 3000
				env:
					- name: GF_SECURITY_ADMIN_PASSWORD
					value: "admin"  # 비밀번호
				volumeMounts:
					- mountPath: /var/lib/grafana  # Grafana의 데이터 저장 경로
					name: grafana-storage
			volumes:
				- name: grafana-storage
				persistentVolumeClaim:
					claimName: grafana-efs-claim  # PVC 이름

		---
		apiVersion: v1
		kind: Service
		metadata:
		name: grafana
		spec:
		type: NodePort  # ClusterIP에서 NodePort로 변경
		ports:
			- port: 3000
			targetPort: 3000
			nodePort: 30098  # 원하는 포트 설정
		selector:
			app: grafana

- 생성한 대쉬보드나 연결 설정 등 저장이 필요하기 때문에 efs 1기가 붙여줌



### 사용법

1. grafana에 prometheus 연동

![alt text](<이미지 27.png>)

2. prometheus의 서비스 이름과 지정한 포트를 입력해준다.

![alt text](<이미지 29.png>)

3. 연결이 잘 됐는지 확인

![alt text](<이미지 30.png>)

4. dashboard로 가서 새로운 폴더나 대쉬보드 생성

![alt text](<이미지 31.png>)

5. 새로운 대쉬보드나 기존의 것을 edit 가능

![alt text](<이미지 39.png>)

![alt text](<이미지 38.png>)

6. 매트릭을 검색하거나 직접 쿼리문 작성

![alt text](<이미지 40.png>)

![alt text](<이미지 36.png>)

이렇게 해서 원하는 정보를 시각화 하여 볼 수 있다.