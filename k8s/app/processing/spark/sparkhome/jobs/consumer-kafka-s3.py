from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, udf
from pyspark.sql.types import StructType, StringType
from datetime import datetime
import os
import hashlib

aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

# Spark 세션 생성
spark = SparkSession.builder \
    .appName("KafkaToS3SignupWithEncryption") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.2,org.apache.hadoop:hadoop-aws:3.3.1") \
    .config("spark.hadoop.fs.s3a.access.key", "aws_access_key") \
    .config("spark.hadoop.fs.s3a.secret.key", "aws_secret_key") \
    .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.EnvironmentVariableCredentialsProvider") \
    .getOrCreate()

# Kafka 메시지에 맞춘 스키마 정의
signup_schema = StructType() \
    .add("name", StringType()) \
    .add("user_id", StringType()) \
    .add("password", StringType())

# 비밀번호 해시 처리 함수
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# UDF로 해시 함수 등록
hash_password_udf = udf(hash_password, StringType())

# Kafka에서 스트리밍 데이터 읽기
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-1:9092,kafka-2:9092,kafka-3:9092") \
    .option("subscribe", "user-topic") \
    .option("startingOffsets", "latest") \
    .load()

# Kafka 메시지의 value를 JSON 형식으로 변환하여 파싱
parsed_df = df.selectExpr("CAST(value AS STRING) as json_value") \
    .select(from_json(col("json_value"), signup_schema).alias("data")) \
    .select("data.*")

# 비밀번호를 해시 처리
hashed_df = parsed_df.withColumn("password", hash_password_udf(col("password")))

current_year = datetime.now().strftime("%Y")
current_month = datetime.now().strftime("%m")
current_day = datetime.now().strftime("%d")


# S3에 데이터를 저장 (Parquet 형식으로 저장)
query = hashed_df.writeStream \
    .format("parquet") \
    .option("path", f"s3a://team06-rawdata/user-data/year={current_year}/month={current_month}/day={current_day}/") \
    .option("checkpointLocation", "s3a://team06-mlflow-feature/etc-data-checkpoint/") \
    .trigger(processingTime="1 minutes") \
    .start()

query.awaitTermination()
