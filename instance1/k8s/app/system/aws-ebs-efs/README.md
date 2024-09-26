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
helm install aws-efs-csi-driver aws-efs-csi-driver/aws-efs-csi-driver --namespace kube-system
```

### CSI 드라이버에서 사용 할 수 있도록  AWS 엑세스 토큰을 secret 리소스로 만들기 
```bash
kubectl create secret generic aws-cli --from-env-file=.env \
  --namespace kube-system
```

### Helm 명령어로 직접 환경 변수 전달

```bash
helm upgrade aws-efs-csi-driver aws-efs-csi-driver/aws-efs-csi-driver \
  --namespace kube-system \
  --set controller.env[0].name=AWS_ACCESS_KEY_ID \
  --set controller.env[0].valueFrom.secretKeyRef.name=aws-cli \
  --set controller.env[0].valueFrom.secretKeyRef.key=AWS_ACCESS_KEY_ID \
  --set controller.env[1].name=AWS_SECRET_ACCESS_KEY \
  --set controller.env[1].valueFrom.secretKeyRef.name=aws-cli \
  --set controller.env[1].valueFrom.secretKeyRef.key=AWS_SECRET_ACCESS_KEY
```