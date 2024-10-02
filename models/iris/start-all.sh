#!/bin/bash

#run all models
echo "run models ... "
DIRECTORY="/home/ubuntu/mlops/models/iris"

echo "pyenv activating ... "

export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

VIRTUAL_ENV_NAME="mlenv"
pyenv activate "$VIRTUAL_ENV_NAME"
python train_and_register_model.py

echo "pyenv deactivating ... "
pyenv deactivate

# build_version.txt 파일로부터 버전 정보 읽기
BUILD_VERSION=$(cat /home/ubuntu/mlops/models/iris/.build_version.txt)

#git push
echo "git push ... "
BRANCH="mlops"
#ORIGIN_BRANCH="instance4"
COMMIT_MESSAGE="model created or edited"

git add /home/ubuntu/mlops/models/iris/.
git commit -m "$COMMIT_MESSAGE - $(date '+%Y-%m-%d %H:%M:%S') - ${BUILD_VERSION}"
git push origin "$BRANCH"

DOCKER_IMAGE="westdragonwon/iris_deploy:${BUILD_VERSION}"

docker build -t ${DOCKER_IMAGE} -f /home/ubuntu/mlops/models/iris/docker_deploy/Dockerfile /home/ubuntu/mlops/models/iris/docker_deploy/
docker push ${DOCKER_IMAGE}

#실행 전 반드시 iris-deployment, iris-container가 필요함
kubectl set image deployment/iris-deployment iris-container=${DOCKER_IMAGE}

