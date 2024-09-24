from pyspark.sql import SparkSession

# Spark 세션 생성
spark = SparkSession.builder \
    .appName("Kafka2Postgres") \
    .getOrCreate()

# Kafka로부터 데이터 읽기
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-1:9092") \
    .option("subscribe", "testL") \
    .load()

# Kafka에서 읽은 데이터의 key와 value를 문자열로 변환
df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

# 데이터 처리 예: value 컬럼 출력
query = df.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

# 스트리밍 쿼리 실행
query.awaitTermination()
