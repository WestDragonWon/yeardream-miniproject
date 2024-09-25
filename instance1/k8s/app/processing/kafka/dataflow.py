import boto3
import os

# S3 클라이언트 생성
s3 = boto3.client('s3')

# 업로드할 디렉토리 경로 및 S3 버킷 정보
directory_path = '/home/ubuntu/yeardream-miniproject/instance1/k8s/app/processing/kafka/'  # 로컬 디렉토리 경로
bucket_name = 'team06-mlflow-feature'  # S3 버킷 이름
s3_directory = 'data-1/iris/'              # S3에 저장할 디렉토리 경로

# 디렉토리 내의 모든 파일을 S3에 업로드
try:
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)  # 전체 파일 경로
        if os.path.isfile(file_path):  # 파일인지 확인
            s3_object_name = os.path.join(s3_directory, filename)  # S3 객체 이름
            s3.upload_file(file_path, bucket_name, s3_object_name)
            print(f"'{file_path}' has been uploaded to '{bucket_name}/{s3_object_name}'")
except Exception as e:
    print(f"Error uploading files: {e}")
