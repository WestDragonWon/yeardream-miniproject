import pandas as pd
import boto3
from rediscluster import RedisCluster
import json
from io import StringIO

# S3 버킷 및 파일 정보
bucket_name = 'team06-mlflow-feature'  # S3 버킷 이름
s3_object_name = 'iris.csv'  # S3 객체 경로

# Redis 클러스터 접속 정보
startup_nodes = [{"host": "192.168.182.16", "port": "6379"}]  # Redis 서비스의 ClusterIP
redis_client = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

# S3에서 CSV 파일 읽기
s3 = boto3.client('s3')
csv_obj = s3.get_object(Bucket=bucket_name, Key=s3_object_name)
body = csv_obj['Body'].read().decode('utf-8')

# 파일 내용을 pandas DataFrame으로 변환
data = pd.read_csv(StringIO(body))

# DataFrame의 각 행을 Redis에 삽입
for index, row in data.iterrows():
    # Redis에 JSON 형태로 저장
    redis_client.set(f"row:{index}", json.dumps(row.to_dict()))

print("Data has been imported to Redis.")
