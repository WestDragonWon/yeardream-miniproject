import pandas as pd
import boto3
from sqlalchemy import create_engine
from io import StringIO

# S3 버킷 및 파일 정보
bucket_name = 'team06-mlflow-feature'  # S3 버킷 이름
s3_object_name = 'iris.csv'  # S3 객체 경로

# PostgreSQL 접속 정보
db_user = 'POSTGRES_USER'      # PostgreSQL 사용자 이름
db_password = 'POSTGRES_PASSWORD'   # PostgreSQL 비밀번호
db_host = '192.168.189.70' 
db_port = '5432'                # PostgreSQL 포트
db_name = 's32db'  # 데이터베이스 이름

# S3에서 CSV 파일 읽기
s3 = boto3.client('s3')
csv_obj = s3.get_object(Bucket=bucket_name, Key=s3_object_name)
body = csv_obj['Body'].read().decode('utf-8')

# 파일 내용을 pandas DataFrame으로 변환
data = pd.read_csv(StringIO(body))

# SQLAlchemy를 사용하여 PostgreSQL 엔진 생성
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# 데이터프레임을 PostgreSQL에 로드
data.to_sql('iris_data', engine, if_exists='replace', index=False)  # 'iris_data'는 테이블 이름
