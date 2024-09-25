import os
import csv
import boto3
from pymongo import MongoClient

# S3와 MongoDB 환경변수에서 시크릿 값 가져오기
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = 'team06-mlflow-feature'
S3_REGION = 'ap-northeast-2'
S3_FILE_KEY = 'iris.csv'  # S3에 있는 CSV 파일의 경로

MONGO_URI = "mongodb://mongodb:27017"  # MongoDB 주소
MONGO_DB = "mongo"  # MongoDB 데이터베이스 이름
MONGO_COLLECTION = "test"  # MongoDB 컬렉션 이름

def fetch_csv_from_s3():
    try:
        s3 = boto3.client('s3', 
                          region_name=S3_REGION,
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_FILE_KEY)
        csv_data = obj['Body'].read().decode('utf-8').splitlines()
        return csv.reader(csv_data)
    except Exception as e:
        print(f"Error fetching data from S3: {e}")
        return None

def insert_data_to_mongo(data):
    if data is None:
        print("No data to insert")
        return

    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]

        header = next(data)  # 첫 번째 행을 헤더로 처리
        for row in data:
            document = {header[i]: row[i] for i in range(len(header))}
            collection.insert_one(document)
        print("Data inserted successfully into MongoDB")
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")

if __name__ == "__main__":
    csv_data = fetch_csv_from_s3()
    insert_data_to_mongo(csv_data)
