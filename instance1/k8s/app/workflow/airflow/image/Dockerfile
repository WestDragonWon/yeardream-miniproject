FROM apache/airflow:2.9.3-python3.8

# root 사용자로 전환
USER root

ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


# rsync 설치
RUN apt-get update && \
    apt-get install -y rsync

# airflow 사용자로 전환
USER airflow


# 추가 패키지 설치 (Kafka 클라이언트 등)
RUN pip install confluent-kafka
RUN pip install boto3 pandas sqlalchemy psycopg2-binary
RUN pip install pymongo
RUN pip install boto3 redis pandas
RUN pip install redis-py-cluster
RUN pip install mlflow

# Airflow 웹서버 시작 명령어
CMD ["airflow", "webserver"]
