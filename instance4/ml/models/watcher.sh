#!/bin/bash

WATCH_DIR="/home/ubuntu/yeardream-miniproject/instance4/ml/models"

inotifywait -m -e create "$WATCH_DIR" --format '%w%f' | while read NEW_FILE
do
    echo "새 파일이 생성되었습니다: $NEW_FILE"
    /home/ubuntu/yeardream-miniproject/instance4/ml/models/runAndPush.sh
    echo "모든 파일을 실행하고, instance4 브랜치에 push 했습니다."
done
