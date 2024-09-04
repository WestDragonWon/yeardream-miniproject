#!/bin/bash

BRANCH_NAME="instance1"

# Git 디렉토리로 이동
cd /home/ubuntu/yeardream-miniproject/

# Git 설정: 사용자 이름과 이메일
git config --global user.name "westdragonwon"
git config --global user.email "westdragonwon@gmail.com"

# 변경사항 커밋 및 푸시
git add .
git commit -m "Automated commit from $BRANCH_NAME at $(date)"
git push yeardream-miniproject $BRANCH_NAME 
