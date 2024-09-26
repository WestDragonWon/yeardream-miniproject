#!/bin/bash

# airflow.cfg 파일에서 default_timezone을 Asia/Seoul로 설정
sed -i "s/default_timezone = utc/default_timezone = Asia\/Seoul/" ${AIRFLOW_HOME}/airflow.cfg

# Airflow의 기본 명령어 실행
exec "$@"
