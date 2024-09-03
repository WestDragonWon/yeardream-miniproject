#!/bin/bash

BRANCH_NAME="instance1"

# Git 레포지토리 경로로 이동
cd /home/ubuntu/yeardream-miniproject/

# Git 상태 확인 후 커밋 및 푸쉬
git add .
git commit -m "Automated push from $BRANCH_NAME at $(date)"
git push yeardream-miniproject $BRANCH_NAME
