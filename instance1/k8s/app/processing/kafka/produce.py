from confluent_kafka import Producer

KAFKA_BROKER = 'kafka-1:9092'  # Kafka 브로커 주소
KAFKA_TOPIC = 'conn'  # 메시지를 보낼 Kafka 토픽

# Kafka Producer 생성
producer = Producer({'bootstrap.servers': KAFKA_BROKER})

# 메시지 전송
try:
    producer.produce(KAFKA_TOPIC, key='test', value='Hello Kafka!')
    producer.flush()  # 메시지를 전송
    print("Message sent successfully!")
except Exception as e:
    print(f"Error occurred: {e}")
