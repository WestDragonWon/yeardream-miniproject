# Storageclass
- 스토리지 클래스란 Kubernetes에서 동적 스토리지 프로비저닝을 지원하기 위해 사용되는 리소스
    - 스토리지를 수동으로 생성하고 관리하는 데 필요한 작업을 줄이고, 애플리케이션 배포의 속도와 효율성을 높입니다.

- 사용자가 PersistentVolumeClaim(PVC)을 생성할 때 이 이름을 참조하여 원하는 스토리지 유형을 지정

- 스토리지의 삭제 정책은 PersistentVolumeClaim이 삭제될 때 EBS 볼륨도 자동으로 삭제되도록 설정되어 있습니다.


StorageClass 리소스의 주요 내용

fsType: ext4
생성된 스토리지 볼륨에 사용할 파일 시스템 유형입니다. 여기서는 ext4 파일 시스템을 사용하도록 지정합니다.
type: gp3
AWS EBS의 경우 ext4가 기본값

reclaimPolicy:
기본값: Delete
설명: PersistentVolume(PV)이 삭제될 때의 동작을 정의합니다. Delete는 PVC가 삭제될 때 PV도 삭제하는 정책이고, Retain은 PVC가 삭제되더라도 PV를 보존하는 정책

provisioner: ebs.csi.aws.com
Kubernetes 클러스터에서 실제로 스토리지를 프로비저닝하는 CSI(Container Storage Interface) 드라이버fh
AWS EBS 볼륨을 동적으로 스토리지를 프로비저닝하는 데 사용할 CSI(Container Storage Interface) 입니다. 

volumeBindingMode: WaitForFirstConsumer
기본값: Immediate
스토리지 볼륨을 생성할 시기를 제어합니다. Immediate는 PVC가 생성되면 즉시 볼륨을 생성합니다. WaitForFirstConsumer는 PVC가 특정 노드에 바인딩될 때까지 (첫 번째 소비자가 있을 때까지) 볼륨 생성을 지연시킵니다. 즉, PersistentVolumeClaim이 특정 노드에 바인딩될 때까지 볼륨이 생성되지 않습니다. 이는 리소스를 최적화하고 스케줄링을 개선하는 데 유용합니다

volumeBindingMode: Immediate
스토리지 프로비저닝의 바인딩 방식을 지정합니다.

Immediate: PersistentVolumeClaim(PVC)이 생성되면 즉시 PersistentVolume(PV)이 할당됩니다. 즉, 사용자가 PVC를 요청할 때, 스토리지가 즉시 프로비저닝됩니다.
이 설정은 볼륨이 특정 노드에 바인딩되지 않고, 클러스터 내의 어느 노드에서도 사용될 수 있는 EFS와 같은 공유 스토리지에 적합합니다.

# ReadWriteOnce로 되어있는거 바꿔주기

- ReadWriteMany  # EFS에 맞는 접근 모드

# EFS에서 생성한 새로운 starageClassName을 넣어주기

storageClassName: # EFS 스토리지 클래스 이름


# 