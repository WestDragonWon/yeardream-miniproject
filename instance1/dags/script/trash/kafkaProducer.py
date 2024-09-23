
from confluent_kafka import Producer

conf = {
    'bootstrap.servers': '10.98.218.95:9092,10.110.230.222:9092,10.101.191.226:9092',
    'enable.idempotence': False
}

producer = Producer(**conf)

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

# Produce a message
producer.produce('testL', key='key', value='your_message', callback=delivery_report)

# Wait for the message to be delivered
producer.flush()

