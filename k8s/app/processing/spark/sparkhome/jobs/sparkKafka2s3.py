from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, regexp_replace, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from datetime import datetime, timedelta
# 카프카 메시지 스키마 정의
schema = StructType([
    StructField("sepal_length", DoubleType(), True),
    StructField("sepal_width", DoubleType(), True),
    StructField("petal_length", DoubleType(), True),
    StructField("petal_width", DoubleType(), True),
    StructField("species", StringType(), True)
])

# 스파크 세션 생성
spark = SparkSession.builder \
    .appName("IrisKafkaToS3") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.2") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# 카프카 large-csv-topic topic 처음부터 읽기
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-1:9092,kafka-2:9092,kafka-0:9092") \
    .option("subscribe", "iris-topic1") \
    .option("startingOffsets", "earliest") \
    .load()

# Json value에서 (")부호 제거
parsed_df = df.select(from_json(
    regexp_replace(col("value").cast("string"), "^\"|\"$", ""),
    schema
).alias("parsed_value"))

filtered_df = parsed_df.filter(
    (col("parsed_value.sepal_length").between(0.5, 30.0)) &
    (col("parsed_value.sepal_width").between(0.3, 10.0)) &
    (col("parsed_value.petal_length").between(0.5, 40.0)) &
    (col("parsed_value.petal_width").between(0.1, 15.0)) &
    (col("parsed_value.species").isin("setosa", "versicolor", "virginica"))
)

output_df = filtered_df.select("parsed_value.*")
current_time = datetime.now()

# Extract the new year, month, day, and hour after adding 9 hours
current_year = current_time.strftime("%Y")
current_month = current_time.strftime("%m")
current_day = current_time.strftime("%d")
current_hour = current_time.strftime("%H")
# S3에 쓰기
query = output_df \
    .writeStream \
    .format("parquet") \
    .option("path", f"s3a://team06-rawdata/iris-data/year={current_year}/month={current_month}/day={current_day}/hour={current_hour}/") \
    .option("checkpointLocation", "s3a://team06-mlflow-feature/iris-csv-checkpoint/") \
    .trigger(processingTime="5 minutes") \
    .start()
query.awaitTermination()
