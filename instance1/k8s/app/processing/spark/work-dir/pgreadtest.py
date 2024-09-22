from pyspark.sql import SparkSession
spark = SparkSession.builder \
        .config("spark.driver.extraClassPath", "/opt/spark/jars/postgresql-42.7.4.jar") \
        .appName("Read PostgreSQL Table") \
        .getOrCreate()

df = spark.read.format("jdbc") \
        .option("url", "jdbc:postgresql://postgres:5432/testdb") \
        .option("driver", "org.postgresql.Driver") \
        .option("dbtable", "test_table") \
        .option("user", "postgres") \
        .load()
df.show(5)
print('@@@@@@@@@@@@@@@@@@')

spark.stop()
