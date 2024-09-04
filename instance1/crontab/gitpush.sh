#!/bin/bash

# 환경 변수 설정
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
export HOME=/home/ubuntu

BRANCH_NAME="instance1"

# SSH 에이전트 실행 및 SSH 키 추가
eval $(ssh-agent -s)
ssh-add /home/ubuntu/.ssh/id_ed25519

# GitHub 호스트 키가 없을 경우 추가
if ! grep -q "^github.com " ~/.ssh/known_hosts; then
  ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts
fi

# Git 디렉토리로 이동
cd /home/ubuntu/yeardream-miniproject/

# Git 설정: 사용자 이름과 이메일
git config --global user.name "westdragonwon"
git config --global user.email "westdragonwon@gmail.com"

# 변경사항 커밋 및 푸시
git add .
git commit -m "Automated commit from $BRANCH_NAME at $(date)"
git push origin $BRANCH_NAME
