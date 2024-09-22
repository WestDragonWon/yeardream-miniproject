from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['10.98.218.95:9092', '10.110.230.222:9092', '10.101.191.226:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    retries=5,  # Retry up to 5 times
    request_timeout_ms=300000,  # Set timeout to 5 minutes
    linger_ms=500,  # Collect messages for up to 500ms before sending
)

data = {'key': 'value'}
producer.send('employee_data', value=data)
producer.flush()

