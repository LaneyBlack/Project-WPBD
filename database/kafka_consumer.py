from confluent_kafka import Consumer, KafkaException

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-consumer-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)

# Subscribe to the topic you expect from Debezium (e.g., 'dbserver1.public.my_table')
consumer.subscribe(['dbserver1.public.your_table_name'])

try:
    while True:
        msg = consumer.poll(1.0)  # timeout in seconds
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())
        else:
            print(f"Received message: {msg.value().decode('utf-8')}")
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    consumer.close()
