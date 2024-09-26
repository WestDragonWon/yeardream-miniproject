from pyspark import SparkConf, SparkContext

conf = SparkConf().setAppName("test-parallelize")

sc = SparkContext(conf=conf)

local_list = list(range(10))
print(f'local_list: {local_list}')
rdd = sc.parallelize(local_list).map(lambda x: x * 2)
output = rdd.collect()
print('\n')
print(f'rdd : {output}')
sc.stop()
