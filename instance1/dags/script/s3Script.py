from kafka import KafkaConsumer
import boto3

# Kafka Consumer
consumer = KafkaConsumer('testL',
                         bootstrap_servers=['kafka-1:9092'],
                         auto_offset_reset='earliest',
                         enable_auto_commit=True,
                         group_id='my-group')

# S3 client
s3 = boto3.client('s3')

for message in consumer:
    # Process message
    data = message.value.decode('utf-8')
    
    # Write to S3
    s3.put_object(Bucket='your-bucket', Key='your-key', Body=data)
