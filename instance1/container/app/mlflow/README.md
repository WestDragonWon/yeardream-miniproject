1. curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 설치 스크립트
 
2. chmod 700 get_helm.sh: 권한 부여
 
3. ./get_helm.sh: 다운로드

4. helm repo add community-charts https://community-charts.github.io/helm-charts
	- 헬름에 새로운 차트 저장소 추가. community-charts라는 저장소 만들고 community-charts여기 있는
	  차트 들을 설치 가능.

5. helm install my-mlflow community-charts/mlflow --version 0.7.19: mlflow 차트를 설치

6. export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=mlflow,app.kubernetes.io/instance=my-mlflow" -o jsonpath="{.items[0].metadata.name}")

	- POD_NAME이라는 환경변수 설정하고 현재 클러스터에 Pod 목록을 가져옴.
	- default에 있는 pod만 검색하고 app.kubernetes.io/name=mlflow,app.kubernetes.io/instance=my-mlflow 이 레이블이 있는 애만 가져오겠다.
	-  -o jsonpath="{.items[0].metadata.name}" 결과를 json으로 출력해서 첫번째 pod 이름만 가져옴.

   export CONTAINER_PORT=$(kubectl get pod --namespace default $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")

	- CONTAINER_PORT라는 환경 변수를 설정. 첫 번째 명령어에서 가져온 POD_NAME에 해당하는 Pod의 정보를 가져옴.
	- Pod의 컨테이너에서 첫 번째 포트의 포트 번호를 가져옴

7. kubectl --namespace default port-forward $POD_NAME 8080:$CONTAINER_PORT : 기존 실행 코드지만 너무 복잡함.

8. 최종 서버 실행 명령어
	
	port_forward 
