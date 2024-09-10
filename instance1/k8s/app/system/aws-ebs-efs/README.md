# EBS CSI 드라이버를 설치합니다.
```bash
## 헬름을 사용한 설치
# 저장소 레파지토리 추가
helm repo add aws-ebs-csi-driver https://kubernetes-sigs.github.io/aws-ebs-csi-driver
helm repo update

# 설치
helm install aws-ebs-csi-driver aws-ebs-csi-driver/aws-ebs-csi-driver --namespace kube-system
```

# EFS CSI 드라이버를 다운로드 및 설치합니다.

```bash
## 헬름을 사용한 설치
# 저장소 레파지토리 추가
helm repo add aws-efs-csi-driver https://kubernetes-sigs.github.io/aws-efs-csi-driver/
helm repo update

## 헬름을 사용한 설치
# 저장소 레파지토리 추가
helm install aws-efs-csi-driver aws-efs-csi-driver/aws-efs-csi-driver --namespace kube-system
```

