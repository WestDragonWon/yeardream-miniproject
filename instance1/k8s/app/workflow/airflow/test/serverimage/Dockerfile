FROM apache/airflow:2.9.3-python3.8

# root 사용자로 전환
USER root

# 한국 시간대로 설정
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# rsync 설치
RUN apt-get update && \
    apt-get install -y rsync

# pod_template.yaml 복사 및 권한 설정
COPY --chown=airflow:airflow pod_template.yaml /opt/airflow/pod_template.yaml

# airflow.cfg에 pod_template_file 설정 추가
RUN echo "[kubernetes]" >> /opt/airflow/airflow.cfg && \
    echo "pod_template_file = /opt/airflow/pod_template.yaml" >> /opt/airflow/airflow.cfg

# airflow 사용자로 전환하여 패키지 설치
USER airflow

# 추가 패키지 설치 (Kafka 클라이언트 등)
RUN pip install confluent-kafka boto3 pandas sqlalchemy psycopg2-binary pymongo redis redis-py-cluster mlflow

# root 사용자로 전환하여 entrypoint.sh 설정
USER root

# entrypoint.sh 스크립트 복사
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# airflow 사용자로 다시 전환
USER airflow

# Airflow 실행 전에 entrypoint.sh 스크립트 실행
ENTRYPOINT ["/entrypoint.sh"]

# Airflow 웹서버 시작 명령어
CMD ["airflow", "webserver"]
