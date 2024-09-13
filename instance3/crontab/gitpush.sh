#!/bin/bash

# 환경 변수 설정
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
export HOME=/home/ubuntu

BRANCH_NAME="instance3"
ENV_PATH="/home/ubuntu/yeardream-miniproject/$BRANCH_NAME/crontab/.env"

# .env 파일 로드 / 검증코드를 포함하여 로드 실패시 에러 메시지 출력
if [ -f "$ENV_PATH" ]; then
  export $(grep -v '^#' "$ENV_PATH" | xargs)
else
  echo ".env file not found at $ENV_PATH"
  exit 1
fi

# Slack 웹훅 URL을 환경 변수로 가져옴
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL}"

# Slack 메시지 전송 함수
send_slack_message() {
  local status="$1"
  local message="$2"

  # 메시지에 이모지 추가
  local icon=""
  if [ "$status" == "Success" ]; then
    icon="✅"  # 성공 이모지
  else
    icon="⚠️"  # 실패 이모지
  fi

  # Slack 메시지 전송
  curl -X POST -H 'Content-type: application/json' --data "{
    \"text\": \"$icon [Git Automation - $BRANCH_NAME] $status: $message\"
  }" "$SLACK_WEBHOOK_URL"
}

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
git config --global user.name "WestDragonWon"
git config --global user.email "westdragonwon@gmail.com"

# 변경사항 커밋 및 푸시
git add .
COMMIT_OUTPUT=$(git commit -m "Automated commit from $BRANCH_NAME at $(date)" 2>&1)
COMMIT_STATUS=$?

if [[ $COMMIT_OUTPUT == *"nothing to commit"* ]]; then
  send_slack_message "No Changes" "No changes to commit on $BRANCH_NAME."
  exit 0
elif [ $COMMIT_STATUS -ne 0 ]; then
  send_slack_message "Failure" "Git commit failed: $COMMIT_OUTPUT"
  exit 1
fi

PUSH_OUTPUT=$(git push origin $BRANCH_NAME 2>&1)
PUSH_STATUS=$?

if [ $PUSH_STATUS -ne 0 ]; then
  send_slack_message "Failure" "Git push failed: $PUSH_OUTPUT"
else
  send_slack_message "Success" "Git push succeeded: $PUSH_OUTPUT"
fi
