from confluent_kafka import Producer
import pandas as pd
import json
import os

KAFKA_TOPIC = 'large-csv-topic'
KAFKA_BOOTSTRAP_SERVERS = ['kafka-1:9092']

# CSV file
CSV_FILE_PATH = './iris_dataset20.csv'

CHUNK_SIZE = 1024*1024

def send_chunk_to_kafka(chunk_number):
    producer = Producer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        max_request_size=10485760  # 10MB, adjust as needed
    )

    start_row = chunk_number * CHUNK_SIZE
    end_row = (chunk_number + 1) * CHUNK_SIZE

    try:
        chunk = pd.read_csv(CSV_FILE_PATH, skiprows=range(1, start_row + 1), nrows=CHUNK_SIZE, header=0)

        for _, row in chunk.iterrows():
            producer.send(KAFKA_TOPIC, value=row.to_dict())

        producer.flush()
        return f"Chunk {chunk_number} sent successfully"
    except Exception as e:
        return f"Error processing chunk {chunk_number}: {str(e)}"
    finally:
        producer.close()

def count_chunks():
    total_rows = sum(1 for _ in open(CSV_FILE_PATH)) - 1
    return (total_rows // CHUNK_SIZE) + (1 if total_rows % CHUNK_SIZE else 0)

chunknum = count_chunks()
for i in range(chunknum):
    send_chunk_to_kafka(i)

