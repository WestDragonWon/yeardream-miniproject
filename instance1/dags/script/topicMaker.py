from confluent_kafka.admin import AdminClient, NewTopic

# Kafka admin configuration (adjust your broker addresses)
admin_conf = {
    'bootstrap.servers': '10.98.218.95:9092,10.110.230.222:9092,10.101.191.226:9092'
}

# Create AdminClient
admin_client = AdminClient(admin_conf)

# Define a new topic (adjust replication factor and partition count)
topic_name = 'employee_data'
new_topic = NewTopic(topic_name, num_partitions=3, replication_factor=2)

# Call create_topics
try:
    result = admin_client.create_topics([new_topic])
    result[topic_name].result()  # Wait for the operation to finish
    print(f"Topic '{topic_name}' created successfully.")
except Exception as e:
    print(f"Failed to create topic: {e}")

