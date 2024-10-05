#!/bin/bash

# pyenv 가상 환경 이름
venv_name="mlenv"

# pyenv 가상 환경을 활성화합니다.
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# pyenv 가상 환경을 활성화합니다.
pyenv activate $venv_name

# requirements.txt 파일 경로
requirements_file="/home/ubuntu/mlops/requirements.txt"

# pip freeze를 사용하여 설치된 패키지 목록을 가져오고 requirements.txt에 저장합니다.
if pip freeze > $requirements_file; then
    echo "$requirements_file가 성공적으로 업데이트되었습니다."
else
    echo "pip freeze 명령어 실행 중 오류 발생."
fi

