from confluent_kafka import Producer

conf ={ 
    'bootstrap.servers': 'kafka-1:9092',
}

producer = Producer(**conf)

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

# Produce a message
producer.produce('testL', key='test', value='message', callback=delivery_report)

# Wait for the message to be delivered
producer.flush()

