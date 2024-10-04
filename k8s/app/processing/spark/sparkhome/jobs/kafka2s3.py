from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, regexp_replace, current_timestamp, year, month, dayofmonth, hour
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

# Define Kafka message schema
schema = StructType([
    StructField("sepal_length", DoubleType(), True),
    StructField("sepal_width", DoubleType(), True),
    StructField("petal_length", DoubleType(), True),
    StructField("petal_width", DoubleType(), True),
    StructField("species", StringType(), True)
])

# Create Spark session
spark = SparkSession.builder \
    .appName("IrisKafkaToS3") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.2,org.apache.hadoop:hadoop-aws:3.3.1") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Read from Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-1:9092,kafka-2:9092,kafka-3:9092") \
    .option("subscribe", "iris-topic") \
    .option("startingOffsets", "earliest") \
    .load()

# Parse JSON value
parsed_df = df.select(from_json(
    regexp_replace(col("value").cast("string"), "^\"|\"$", ""),
    schema
).alias("parsed_value"))

# Select columns and add timestamp
output_df = parsed_df.select("parsed_value.*") \
    .withColumn("processing_time", current_timestamp())

# Write to S3
query = output_df \
    .writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "s3a://team06-rawdata/iris-data") \
    .option("checkpointLocation", "s3a://team06-mlflow-feature/iris-csv-checkpoint/") \
    .partitionBy(
        year("processing_time"),
        month("processing_time"),
        dayofmonth("processing_time"),
        hour("processing_time")
    ) \
    .trigger(processingTime="5 minutes") \
    .start()

query.awaitTermination()
