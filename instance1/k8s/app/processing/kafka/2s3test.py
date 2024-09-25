import boto3
import os

# S3 클라이언트 생성
s3 = boto3.client('s3')

# 업로드할 CSV 파일 경로 및 S3 버킷 정보
file_path = '/home/ubuntu/yeardream-miniproject/instance1/k8s/app/processing/kafka/iris.csv'  # 로컬 CSV 파일 경로
bucket_name = 'team06-mlflow-feature'      # S3 버킷 이름
s3_object_name = 'data-1/iris/iris.csv'

# 파일 업로드
try:
    s3.upload_file(file_path, bucket_name, s3_object_name)
    print(f"'{file_path}' has been uploaded to '{bucket_name}/{s3_object_name}'")
except Exception as e:
    print(f"Error uploading file: {e}")
