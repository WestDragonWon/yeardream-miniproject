# 베이스 이미지 설정 (Python 3.9)
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 설치
COPY . .

RUN pip install -r requirements.txt


# 포트 노출
EXPOSE 5001

# Flask 서버 실행
CMD ["python", "deploy_model.py"]
