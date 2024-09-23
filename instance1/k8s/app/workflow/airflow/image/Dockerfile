FROM apache/airflow:2.9.3-python3.8

# root 사용자로 전환
USER root

# rsync 설치
RUN apt-get update && apt-get install -y rsync

# Airflow 실행에 필요한 사용자로 다시 전환
USER airflow

# Airflow 웹서버 시작 명령어
CMD ["airflow", "webserver"]
