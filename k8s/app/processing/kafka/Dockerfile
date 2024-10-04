# Dockerfile
FROM python:3.11.9

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 설치
RUN pip install --no-cache-dir confluent_kafka

# ConfigMap에서 스크립트를 복사
COPY produce.py .

# 기본 명령어 설정
CMD ["python", "-u", "produce.py"]
