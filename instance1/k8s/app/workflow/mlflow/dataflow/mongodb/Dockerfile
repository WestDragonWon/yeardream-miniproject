# 베이스 이미지로 Python 3.9 사용
FROM python:3.9

# 작업 디렉토리 생성
WORKDIR /app

# 필요한 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Python 코드 복사
COPY . .

# 컨테이너 시작 시 Python 스크립트 실행
CMD ["python", "test.py"]
