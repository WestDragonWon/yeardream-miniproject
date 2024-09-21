import os
from pyspark.sql import SparkSession

aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

spark = SparkSession.builder \
        .appName("readCSV") \
        .config("spark.hadoop.fs.s3a.access.key", aws_access_key) \
        .config("spark.hadoop.fs.s3a.secret.key", aws_secret_key) \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.2.0,com.amazonaws:aws-java-sdk-bundle:1.11.888") \
        .getOrCreate()

csv_file_path = "s3a://team06-mlflow-feature/data/employees.csv"

df = spark.read.csv(csv_file_path, header=True, inferSchema=True)

head(df)

spark.stop()
