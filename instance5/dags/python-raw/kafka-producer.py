import pyarrow.parquet as pq
import pyarrow as pa
from confluent_kafka import Producer
import pandas as pd

# Kafka producer configuration
producer = Producer({'bootstrap.servers': 'localhost:9092'})

# Define chunk size
chunk_size = 1000000  # Number of rows per chunk

# Define a callback function for delivery reports
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Read the Parquet file
parquet_file = 'title_akas_combined.parquet'
parquet_reader = pq.ParquetFile(parquet_file)

# Process each chunk
for batch in parquet_reader.iter_batches(batch_size=chunk_size):
    # Convert batch to Pandas DataFrame
    df = batch.to_pandas()
    
    # Send each row of the dataframe to Kafka
    for index, row in df.iterrows():
        message = row.to_json()  # Convert row to JSON
        producer.produce('my_topic', key=str(index), value=message, callback=delivery_report)

# Wait for any outstanding messages to be delivered
producer.flush()

