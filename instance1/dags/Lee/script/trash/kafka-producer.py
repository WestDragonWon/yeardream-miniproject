import pyarrow.parquet as pq
import pyarrow as pa
from confluent_kafka import Producer
import pandas as pd
import argparse

producer = Producer({'bootstrap.servers': 'kafka-1:9092'})

chunk_size = 1000000  

#에러 확인용 콜백함수
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

#데이터파일경로, 토픽이름 파라미터로 설정
parser = argparse.ArgumentParser()
parser.add_argument('file_path', type=str)
parser.add_argument('topic', type=str)
args = parser.parse_args() 

parquet_file = args.file_path
parquet_reader = pq.ParquetFile(parquet_file)

#배치사이즈만큼 잘라서producing 
for batch in parquet_reader.iter_batches(batch_size=chunk_size):
    df = batch.to_pandas()
    
    for index, row in df.iterrows():
        message = row.to_json() 
        producer.produce(args.topic, key=str(index), value=message, callback=delivery_report)

producer.flush()

