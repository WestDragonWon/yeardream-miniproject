from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, regexp_replace
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

# Define the schema of your Kafka messages
schema = StructType([
    StructField("idx", IntegerType(), True),
    StructField("Sepal.Length", DoubleType(), True),
    StructField("Sepal.Width", DoubleType(), True),
    StructField("Petal.Length", DoubleType(), True),
    StructField("Petal.Width", DoubleType(), True),
    StructField("Species", StringType(), True)
])

# Create Spark Session with Kafka dependency
spark = SparkSession.builder \
    .appName("IrisKafkaToS3") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.2") \
    .getOrCreate()

# Read from Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-1:9092,kafka-2:9092,kafka-3:9092") \
    .option("subscribe", "large-csv-topic") \
    .load()

# Clean double quotes from Kafka message values
parsed_df = df.select(from_json(
    regexp_replace(col("value").cast("string"), "^\"|\"$", ""),
    schema
).alias("parsed_value"))
# Select the fields you want to write to S3
output_df = parsed_df.select("parsed_value.*")
# Write to S3
query = output_df \
    .writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "s3a://team06-mlflow-feature/iris-csv-data/") \
    .option("checkpointLocation", "s3a://team06-mlflow-feature/iris-csv-checkpoint/") \
    .start()

query.awaitTermination()

