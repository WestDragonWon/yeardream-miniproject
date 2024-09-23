from pyspark.sql import SparkSession

# Spark 세션 생성
spark = SparkSession.builder \
    .appName("Kafka2Postgres") \
    .getOrCreate()

# Kafka로부터 데이터 읽기
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-1:9092") \
    .option("subscribe", "cconntest") \
    .load()

# 데이터 변환 및 PostgreSQL로 쓰기
def write_to_postgres(df, epoch_id):
    df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://postgres:5432/test") \
        .option("dbtable", "test") \
        .option("user", "mlops_user") \
        .option("password", "1234") \
        .mode("append") \
        .save()

query = df.selectExpr("CAST(value AS STRING)") \
    .writeStream \
    .foreachBatch(write_to_postgres) \
    .start()

query.awaitTermination()
