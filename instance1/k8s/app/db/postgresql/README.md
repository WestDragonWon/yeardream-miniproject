---
apiVersion: v1 # Kubernetes API 버전 지정
kind: PersistentVolume # 이 리소스가 PersistentVolume임을 명시
metadata:
  name: postgres-pv # PersistentVolume의 이름 지정
spec:
  capacity:
    storage: 1Gi # 스토리지 용량을 1 기가바이트로 설정
  volumeMode: Filesystem # 파일시스템 모드로 볼륨 사용 말그래도 모드를 설정하나봄 ..
  accessModes:
    - ReadWriteMany # 여러 노드에서 읽기/쓰기 가능하도록 설정 ReadWriteOnece는 하나에서만 가능하다. 다른 노드에서 접근이 불가능함. 동시 쓰기가 불가능.
  persistentVolumeReclaimPolicy: Retain # PV 삭제 시 데이터 유지 # Delete로 설정하면 데이터 삭제
  storageClassName: efs-sc # EFS 스토리지 클래스 사용
  csi:
    driver: efs.csi.aws.com # AWS EFS CSI 드라이버 사용
    volumeHandle: fs-00fb81d888c7ed27c # 특정 EFS 볼륨 지정
    #AWS EFS CSI 드라이버에서 사용되는 EFS 파일 시스템 ID (여기서는 fs-00fb81d888c7ed27c)는 AWS 콘솔이나 AWS CLI를 통해 확인할 수 있다 > 일반 계정으로는 확인 불가능 한듯. 


apiVersion: v1 # Kubernetes API 버전 지정
kind: PersistentVolumeClaim # 이 리소스가 PersistentVolumeClaim임을 명시 #관련 사담 : 꿈을 꿨는데 PVC라는 주식이 만원까지 올랐음.
metadata:
  name: postgres-pvc # PersistentVolumeClaim의 이름 지정
spec:
  accessModes:
    - ReadWriteMany # 여러 노드에서 읽기/쓰기 가능하도록 설정 
  storageClassName: efs-sc # EFS 스토리지 클래스 사용
  resources:
    requests:
      storage: 1Gi # 1 기가바이트의 스토리지 요청
#PV와 PVC는 도서관과 도서보관신청서 ..? PV는 관리자가 준비하고 관리하며 이용자는 신청서를 작성하여 어느정도의 보관(공간 및 구성)을 명시하고 PV가 적정한 책장을 찾아 할당함 ..
#PV는 사용 가능한 저장 공간이고, PVC는 그 공간을 사용하기 위한 요청. 이 시스템을 통해 사용자는 복잡한 저장소 세부사항을 몰라도 필요한 저장 공간을 쉽게 사용할수 있게함.. 우리는 도서관 전체를 요청..

apiVersion: apps/v1 # Kubernetes apps API 버전 지정
kind: StatefulSet # 이 리소스가 StatefulSet임을 명시 * Deployment가 아닌 Statefulset을 사용하는 이유는 모든 복제본에 대한 볼륨을 생성 * 데이터 백업에서 중요한 기능이라고 생각됨.. 사견임
metadata:
  name: postgres # StatefulSet의 이름 지정
spec:
  serviceName: "postgres" # 연관된 서비스 이름 지정
  replicas: 2 # Pod 복제본 수를 2개로 설정 () *-0.-1로 복제. 각각 pod 구성 후 복제 정상 작동 여부 시도시 postgre 강제 종료 및 CrashloopBackoff 발생. 데이터 초기화 불가능으로 POD 초기화함.
  selector:
    matchLabels:
      app: postgres # 이 라벨을 가진 Pod 선택
  template:
    metadata:
      labels:
        app: postgres # Pod에 적용할 라벨 지정
    spec:
      containers:
      - name: postgres # 컨테이너 이름 지정
        image: postgres:13 # PostgreSQL 13 버전 이미지 사용 * latest 또는 중간 것 사용?
        ports:
        - containerPort: 5432 # PostgreSQL 기본 포트 노출
        envFrom:
        - secretRef:
            name: db # 'db'라는 이름의 Secret에서 환경 변수 가져오기 * 클러스터 구성 및 Postgre 접속시 여러 환경변수를 사용하니 이것 말도고 많이 필요한거같다. 
        volumeMounts:
        - name: postgres-storage # 마운트할 볼륨 이름
          mountPath: /var/lib/postgresql/data_temp # 컨테이너 내 마운트 경로 ★ 관련해서 이슈가 많았고 제대로 해결하지 못했다 .. 이게 뭐라고 ..
# PostgreSQL는 데이터 디렉토리가 비어있지 않으면 새로운 데이터 베이스 클러스터 초기화하지않음(일종의 안전장치). data 폴더가 뭔가 있는상태로 지우고 재지정 하면 될듯.
# data_temp로 경로를 새로 지정하고 data 폴더 확인 결과 이미 초기화가 된 상태. 해당 디렉토리를 완전히 삭제 후 기존 리소스를 삭제해야 폴더 지정이 다시 될듯 하다. 보류 ..
# 클러스터 구성 전 yaml로 백업 .. 경로 문제때문에 다시 안될 수 도 있다 .. 경로는 이전 사용 경로였는데 문제없이 running 됨 ..
# 일단 경로 data로 다시 지정해보고 클러스터 구성 시도 > data 쪽은 뭔가 막힌 듯 바로 crashloopbackoff 뜸 .. > data_temp로 임시경로 지정 > data 기본경로상 문제가 있는 것 같다.
# spec.persistentVolumeReclaimPolicy: Retain 이라서 기존 데이터때문에 초기화가 안되는건지? 권한문제? (EFS? 이건 권한 받은건데 ..)
# 999라는 데이터폴더 생성 권한이 필요하다. data는 기본 경로 이므로..
        resources:
          requests:
            cpu: 500m # 최소 0.5 CPU 코어 요청
            memory: 1Gi # 최소 1 기가바이트 메모리 요청
          limits:
            cpu: 1 # 최대 1 CPU 코어 사용 제한
            memory: 2Gi # 최대 2 기가바이트 메모리 사용 제한
      volumes:
      - name: postgres-storage # 볼륨 이름 지정
        persistentVolumeClaim:
          claimName: postgres-pvc # 사용할 PVC 이름 지정


apiVersion: v1 # Kubernetes API 버전 지정
kind: Service # 이 리소스가 Service임을 명시
metadata:
  name: postgres # 서비스 이름 지정
spec:
  selector:
    app: postgres # 이 라벨을 가진 Pod 선택
  ports:
    - protocol: TCP # TCP 프로토콜 사용
      port: 5432 # 서비스 포트
      targetPort: 5432 # 대상 Pod의 포트
  clusterIP: None  # Headless 서비스로 설정 (StatefulSet용) 각 데이터베이스 노드에 직접 접근해야하는 경우 사용한다고 함.


ConfigMap 설명

apiVersion: v1: Kubernetes API 버전을 지정
kind: ConfigMap: 이 리소스가 ConfigMap임을 정의
metadata:: ConfigMap의 메타데이터를 정의
ame: postgres-config: ConfigMap의 이름을 "postgres-config"로 지정
data:: ConfigMap에 저장될 데이터를 정의합니다.
postgresql.conf: |: PostgreSQL 설정 파일 내용을 정의

apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-config
data:
  postgresql.conf: |
    listen_addresses = '*'           # 모든 IP 주소에서의 연결을 허용 # 상황에 따라 특정 IP 지정해야겠다.
    wal_level = replica              # 복제를 위한 WAL(Write-Ahead Logging) 레벨 설정
    max_wal_senders = 10             # 동시에 실행될 수 있는 최대 WAL 송신 프로세스 수
    wal_keep_segments = 64           # 보관할 WAL 세그먼트 파일의 최소 개수
  pg_hba.conf: |
    local all all trust              # 로컬 연결은 모든 사용자에 대해 신뢰 (보안상 주의 필요)
    host all all all scram-sha-256   # 모든 데이터베이스, 모든 사용자에 대해 scram-sha-256 인증 사용
    host replication all all scram-sha-256  # 복제 연결에 대해 scram-sha-256 인증 사용
    host replication replicator 192.168.0.0/16 scram-sha-256  # 특정 IP 범위의 복제 연결 허용
# EBS > EFS 전환 전 사용한 ConfigMap이다. 웬만한 연결을 허용했음에도 불구하고 연결관련 오류로 제대로 해결하지못했다. 
# scram-sha-256인증?
비밀번호 저장: 사용자의 비밀번호는 서버에 평문으로 저장되지 않음. 대신, salt와 함께 해시된 형태로 저장
# 인증 과정:
a. 클라이언트가 연결을 요청합니다.
b. 서버는 랜덤 nonce와 저장된 salt를 클라이언트에게 전송합니다.
c. 클라이언트는 사용자의 비밀번호, 서버의 nonce, salt를 사용하여 응답을 생성합니다.
d. 서버는 받은 응답을 검증하여 인증을 완료합니다.
# 채널 바인딩: TLS 연결과 인증 과정을 바인딩하여 추가적인 보안을 제공할 수 있습니다. > 무슨말이지 .. 아무튼 보안이 강화됨..
# > 좋은 비유적인 설명으로는 여권(인증)과 입국 스탬프(TLS 연결)을 동시에 확인하는 것과 유사하다 라는 개념으로 이해하기 좋다..

# 헷갈렷던 것 .. ?
POD를 지정해줘야하는이유
우리는 워크로드 API를 Statefulset을 사용하고 있기때문에.
Statefulset은 각 Pod의 역할이 다르다 > 특정 pod와 연결해야하는 경우가 많다. > 어떤 상황인지는 .. 잘? data pipe line을 구축 후 연동하면 알게될지..
> 필요한 역할의 서버에만 연결할 수 있기때문임.

*Postgres 클러스터링 구성 실패 이유에 대해 생각 및 독백.,..
# 환경변수 및 각종 비밀번호 연동 누락? 최대한 간략하게 세팅했다고 생각하는데도 진행 불가 ..?
# 클러스터링 구성시 작성해야하는 ConfigMap관련 개념 이해 실패 (ex 암호화 방법.. )
# 결과적으로는 .. 클러스터링 개념 부족.. 시간이 부족하지 않았던 것같은데 .. 한게 없다..
# 내용을 정리하면서 알 수 있는 개념이 많은데 그 부분에서 열심히 하지 않아서 .. readme를 작성하면서 알아가는게 더 많은 기분.. 
.
.
.
# pod pv pvc statefulset 등 .. Delete Apply 반복 후 멘탈 붕괴로 감각 과부하 및 집중력 저하 .. 노오력이 부족하다.
~09/12(목)