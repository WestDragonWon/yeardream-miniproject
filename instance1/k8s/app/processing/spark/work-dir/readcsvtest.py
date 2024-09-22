from pyspark.sql import SparkSession

spark = SparkSession.builder \
        .appName("ReadLocalCSV") \
        .getOrCreate()

csv_file_path = "/opt/spark/data/master_doodle_dataframe.csv"

df = spark.read.csv(csv_file_path, header=True, inferSchema=True)

df.show(5)

spark.stop()
