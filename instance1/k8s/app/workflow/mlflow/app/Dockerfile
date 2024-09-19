# 베이스 이미지
FROM python:3.11.9-slim

# 작업 디렉토리 설정
WORKDIR /home/ubuntu/yeardream-miniproject/instance1/k8s/app/workflow/mlflow/app

# 의존성 파일 복사
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 복사
COPY . .

# FastAPI 실행
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]