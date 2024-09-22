from pyspark.sql import SparkSession
import time

spark = SparkSession.builder \
        .appName('test_cluster_01')\
        .getOrCreate()

for i in range(10):
    start_time = time.time()
    time.sleep(3)
    end_time = time.time()
    print(time.time())

print(f"@@@@@@@@@@@@@@@@@@@@@@@@@@@@{end_time - start_time}")

spark.stop()
