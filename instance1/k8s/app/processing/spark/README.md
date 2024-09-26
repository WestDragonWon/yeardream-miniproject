
## 목차

1. [개요](#개요)
2. [사전 요구 사항](#사전-요구-사항)
3. [구성 요소](#구성-요소)
4. [설치 방법](#설치-방법)
5. [사용 방법](#사용-방법)
6. [구현](#구현)

## 개요

Kubernetes 안에 Stand Alone 형식으로 Spark Cluster 환경을 구성하려고 했으나 실패했습니다.

Master 역할을 할 파드를 하나 띄우고, Worker 역할을 할 파드 세개를 띄운 뒤 서로 연결하였지만, Master에서 Job submit시 워커에 Executor가 생성되지 않는 문제를 겪었습니다.

로컬 서버에 스파크를 설치하고, 마스터를 쿠버네티스 API 서버로 설정하여 워커 파드를 동적으로 만드는 방법을 사용하는 방법으로 해결하는 중입니다.

초기 구상 : ![alt text](<img/Pasted image 20240924144004.png>)

## 사전 요구 사항

- Kubernetes 클러스터
- EFS 파일 시스템
- 클러스터에 설치된 EFS CSI 드라이버
- SPARK에서 사용할 jar 파일, Job 파일 등 필요에 따라 커스텀

## 구성 요소

- Spark 클러스터를 위한 Master, Worker의 Deployment, Service
- (선택) jar, py 파일 등 커스텀 파일을 마운트 할 EFS
- (EFS를 선택한 경우) EFS를 사용하기위한 PersistentVolume, PersistentVolumeClaim

## 설치 방법

1. 저장소를 클론합니다. 파일은 instance1/k8s/app/processing/spark에 위치합니다.:
   ```
   git clone https://github.com/WestDragonWon/yeardream-miniproject.git
   cd instance1/k8s/app/processing/spark
   ```

2. 구성을 적용합니다:
   ```
       EFS를 사용하는 경우 : kubectl apply -f spark-pv.yaml
   kubectl apply -f master.yaml
   kubectl apply -f worker.yaml
   ```

## 사용 방법

- SPARK master 인스턴스에 연결 :
  ```
  kubectl exec -it <SPARK-master 파드 이름> /bin/bash
  ```

- 잡 제출 (Stand alone의 클라이언트 모드) - Executor 생성에 실패 :
  ```
  /opt/spark/bin/spark-submit \
  --master spark://spark-master-service:7077 \
  --conf spark.driver.host=spark-master-service \
  --conf spark.driver.bindAddress=0.0.0.0 \
  --deploy-mode client \
  /<잡이 위치한 경로>
    ```

- 잡 제출 (로컬 모드) :
```
  /opt/spark/bin/spark-submit <잡이 위치한 경로>
```


## 구현

파일 명 : spark-pv.yaml
목적 : jar, job이 저장된 EFS를 Pod들과 연결한다.
내용 :
```
apiVersion: v1
kind: PersistentVolume
metadata:
  name: spark-jars-pv
spec:
  capacity:
    storage: 3Gi  # 스토리지 크기 (EFS는 실제 크기 제한 없음)
  volumeMode: Filesystem
  accessModes:
    - ReadWriteMany  # Master, Worker 등 다수의 Pod에서 접근 가능
  persistentVolumeReclaimPolicy: Retain  # PVC가 삭제되어도 PV 유지 (EFS와 연동하였으므로 Delete여도 될 것으로 예상)
  storageClassName: spark-storageclass  # 수정된 StorageClass 이름
  csi:
    driver: efs.csi.aws.com
    volumeHandle: fs-00fb81d888c7ed27c::fsap-0d9a6814ce62a4ba1  # <jar 파일이 저장된 EFS ID>::<경로>
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: spark-jobs-pv
spec:
  capacity:
    storage: 1Gi  # 스토리지 크기 (EFS는 실제 크기 제한 없음)
  volumeMode: Filesystem
  accessModes:
    - ReadWriteMany  # Master, Worker 등 다수의 Pod에서 접근 가능
  persistentVolumeReclaimPolicy: Retain  # PVC가 삭제되어도 PV 유지 (EFS와 연동하였으므로 Delete여도 될 것으로 예상)
  storageClassName: spark-storageclass  # 수정된 StorageClass 이름
  csi:
    driver: efs.csi.aws.com
    volumeHandle: fs-00fb81d888c7ed27c::fsap-0a5131b6e82bd3039  # <job 파일이 저장된 EFS ID>::<경로>
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: spark-jars-pvc
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: spark-storageclass
  resources:
    requests:
      storage: 3Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: spark-jobs-pvc
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: spark-storageclass
  resources:
    requests:
      storage: 1Gi
```

파일 명 : master.yaml
목적 : Spark 클러스터의 master 역할을 할 Deployment, Service를 만든다.
내용 :
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spark-master-deployment
  labels:
    app: spark
spec:
  replicas: 1
  selector:
    matchLabels:
      app: spark
      role: master
  template:
    metadata:
      labels:
        app: spark
        role: master
    spec:
      containers:
      - name: spark-master-container
        image: apache/spark:3.5.1
        ports:
        - containerPort: 7077    #master, worker가 통신할 포트
        - containerPort: 4040    #제출된 Job을 웹으로 확인하기 위한 포트
        - containerPort: 8080    #클러스터 구성을 확인하기 위한 포트
        env:    #스파크 모드를 지정하고, AWS 및 PG에 접속하기 위한 환경 변수 설정
        - name: SPARK_MODE
          value: "master"
        - name: AWS_ACCESS_KEY_ID    
          valueFrom:
            secretKeyRef:
              name: workflow
              key: AWS_ACCESS_KEY_ID
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: workflow
              key: AWS_SECRET_ACCESS_KEY
        - name: POSTGRES_USERNAME    
          valueFrom:
            secretKeyRef:
              name: workflow
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: workflow
              key: POSTGRES_PASSWORD
        - name: SPARK_LOCAL_IP    #파드의 IP를 환경변수로 설정하기 위한 부분
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
            #- name: SPARK_WORKER_INSTANCES
            #value: "3"
        command: ["/opt/spark/bin/spark-class", "org.apache.spark.deploy.master.Master"]
        args: ["--host", "$(SPARK_LOCAL_IP)", "--port", "7077", "--webui-port", "8080"]
        #마스터로 사용하기위한 명령어, 이 명령어가 잘못되어서 executor가 생성이 안 되는 것일 수도 있다.
        volumeMounts:    #jars는 반드시 /opt/spark/jars에 위치해야 스파크가 인식할 수 있다.
        - name: spark-jars-volume
          mountPath: /opt/spark/jars
        - name: spark-jobs-volume
          mountPath: /opt/spark/work-dir
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "500m"
            memory: "1Gi"
      volumes:
      - name: spark-jars-volume
        persistentVolumeClaim:
          claimName: spark-jars-pvc
      - name: spark-jobs-volume
        persistentVolumeClaim:
          claimName: spark-jobs-pvc

      #nodeSelector:
        #type: master
---
apiVersion: v1
kind: Service
metadata:
  name: spark-master-service   ##!!!!반드시!!! spark-master라고 하면 안됨. spark가 사용하는 환경변수 이름이 SPARK_MASTER_PORT인데, 서비스 이름을 spark-master라고 지정하면 쿠버네티스도 같은 이름으로 다른 내용의 변수를 생성
  labels:
    app: spark
spec:
  type: NodePort
  ports:
  - name: spark-master-port    #마스터와 워커끼리 통신할 포트
    port: 7077
    targetPort: 7077
    nodePort: 32077
  - name: spark-master-ui      #클러스터 구성을 확인하기 위한 포트
    port: 8080
    targetPort: 8080
    nodePort: 32080
  - name: spark-master-ui2     #제출된 잡 상태를 확인하기 위한 포트
    port: 4040
    targetPort: 4040
    nodePort: 32040
  selector:
    app: spark
    role: master
```

파일 명 : worker.yaml
목적 : Spark 클러스터의 worker 역할을 할 Deployment, Service를 만든다.
내용 :
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spark-worker-deployment
  labels:
    app: spark
spec:
  replicas: 3
  selector:
    matchLabels:
      app: spark
      role: worker
  template:
    metadata:
      labels:
        app: spark
        role: worker
    spec:
      serviceAccountName: spark  # ServiceAccount를 지정
      containers:
      - name: spark-worker-container
        image: apache/spark:3.5.1
        ports:                  #워커 상태를 확인하기 위한 포트
        - containerPort: 8081
        env:  #스파크 모드를 지정하고, AWS 및 PG에 접속하기 위한 환경 변수 설정
        - name: SPARK_MODE
          value: "worker"
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: workflow
              key: AWS_ACCESS_KEY_ID
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: workflow
              key: AWS_SECRET_ACCESS_KEY
        - name: POSTGRES_USERNAME
          valueFrom:
            secretKeyRef:
              name: workflow
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: workflow
              key: POSTGRES_PASSWORD
        - name: SPARK_LOCAL_IP  #파드의 IP를 환경변수로 지정
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        command: ["/opt/spark/bin/spark-class", "org.apache.spark.deploy.worker.Worker"]
        args: ["spark://spark-master-service:7077", "--host", "$(SPARK_LOCAL_IP)", "--webui-port", "8081"]
        #워커로 설정하기 위한 명령어, 이 명령어가 잘못되어서 executor가 생성이 안 되는 것일 수도 있다.
        volumeMounts:  #jars는 반드시 /opt/spark/jars에 위치해야 스파크가 인식할 수 있다.
          #- name: spark-jars-volume
          #mountPath: /opt/spark/jars
        - name: spark-jobs-volume
          mountPath: /opt/spark/work-dir
        resources:    #메모리 리소스가 부족하여 executor가 생성이 안 되는 가능성도 있어서 넉넉하게 설정해보았다.
          requests:
            cpu: "1"
            memory: "3Gi"
          limits:
            cpu: "1"
            memory: "3Gi"
      volumes:
        #- name: spark-jars-volume
        #persistentVolumeClaim:
        #  claimName: spark-jars-pvc
      - name: spark-jobs-volume
        persistentVolumeClaim:
          claimName: spark-jobs-pvc
      nodeSelector:
        type: worker

---
apiVersion: v1
kind: Service
metadata:
  name: spark-worker-service
  labels:
    app: spark
spec:
  type: NodePort
  ports:
  - name: spark-worker-ui
    port: 8081
    targetPort: 8081
    nodePort: 32081
  selector:
    app: spark
    role: worker

```

## 트러블 슈팅
현상 : 잡 제출시 포트가 int 형식 7077이 아닌 string 형식"spark://spark-master:7077"로 입력되는 현상 발생
원인 : spark 에서는 SPARK_MASTER_PORT 환경변수를 7077로 지정하는 방식으로 포트를 찾는다. service name을 spark-master로 작성시 이 환경변수가 덮어씌워지므로 반드시 서비스의 이름을 spark-master와 다르게 만들어야 한다.
