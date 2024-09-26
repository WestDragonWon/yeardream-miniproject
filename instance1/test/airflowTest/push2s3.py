import boto3
import argparse

#데이터파일경로, s3버켓이름, 버켓경로를 주고 실행하는 함수
def upload_file_to_s3(file_path, bucket_name, s3_key):
    s3_client = boto3.client('s3')
    
    s3_client.upload_file(file_path, bucket_name, s3_key)
    
    print(f'File uploaded to S3://{bucket_name}/{s3_key}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a file to S3")
    
    parser.add_argument('file_path', type=str, help="Path to the local file")
    parser.add_argument('s3_key', type=str, help="S3 key for the uploaded file")
    # 기본 team06-mlflow-feature 버켓사용
    parser.add_argument('--bucket', type=str, default='team06-mlflow-feature', help="S3 bucket name (default: 'team06-mlflow-feature')")
    
    args = parser.parse_args()
    
    upload_file_to_s3(args.file_path, args.bucket, args.s3_key)

