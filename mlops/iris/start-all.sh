#!/bin/bash

source /home/ubuntu/.bashrc

echo "run models ... "
DIRECTORY="/home/ubuntu/mlops/mlops/iris"

echo "pyenv activating ... "

export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"


VIRTUAL_ENV_NAME="mlenv"
pyenv activate "$VIRTUAL_ENV_NAME"

port=5432
if lsof -i TCP:$port >/dev/null; then
    echo "port forward skip"
else
    echo "port forwarding..."
    nohup kubectl port-forward svc/postgres 5432:5432 --address 0.0.0.0 > /home/ubuntu/mlops/crontab/logs/port_forward/port_forward.log 2>&1 &
fi

ENV_PATH="/home/ubuntu/mlops/mlops/iris/.env"

# .env 파일 로드 / 검증코드를 포함하여 로드 실패시 에러 메시지 출력
if [ -f "$ENV_PATH" ]; then
  set -a  # 자동으로 export 되도록 설정
  source "$ENV_PATH" || { echo "Failed to load .env file"; exit 1; }
  set +a  # 자동 export 설정 해제
else
  echo ".env file not found at $ENV_PATH"
  exit 1
fi


POSTGRES_HOST="${POSTGRES_HOST}"
POSTGRES_PORT="${POSTGRES_PORT}"
POSTGRES_DB="${POSTGRES_DB}"
POSTGRES_USER="${POSTGRES_USER}"
POSTGRES_TABLE="${POSTGRES_TABLE}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD}"

python /home/ubuntu/mlops/mlops/iris/train_and_register_model.py

echo "pyenv deactivating ... "
pyenv deactivate


# build_version.txt 파일로부터 버전 정보 읽기
BUILD_VERSION=$(cat /home/ubuntu/mlops/mlops/iris/.build_version.txt)

#git push
echo "git push ... "
BRANCH="mlops"
#ORIGIN_BRANCH="instance4"
COMMIT_MESSAGE="model created or edited"

TARGET_DIR="/home/ubuntu/mlops/mlops/iris/"
cd $TARGET_DIR || exit 1
git add .
git commit -m "$COMMIT_MESSAGE - $(date '+%Y-%m-%d %H:%M:%S') - ${BUILD_VERSION}"
git push origin "$BRANCH"


DOCKER_IMAGE="westdragonwon/iris_deployment:latest"
docker build -t ${DOCKER_IMAGE} -f /home/ubuntu/mlops/mlops/iris/docker_deploy/Dockerfile /home/ubuntu/mlops/mlops/iris/docker_deploy/
docker push ${DOCKER_IMAGE}

DOCKER_IMAGE="westdragonwon/iris_deployment:${BUILD_VERSION}"

docker build -t ${DOCKER_IMAGE} -f /home/ubuntu/mlops/mlops/iris/docker_deploy/Dockerfile /home/ubuntu/mlops/mlops/iris/docker_deploy/
docker push ${DOCKER_IMAGE}


#실행 전 반드시 iris-deployment, iris-container가 필요함
kubectl set image deployment/iris-deployment iris-container=${DOCKER_IMAGE}

