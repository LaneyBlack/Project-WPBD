import os

from confluent_kafka import Producer
from dotenv import load_dotenv

load_dotenv()

conf = {
    'bootstrap.servers': f'{os.getenv("KAFKA_HOST")}:{os.getenv("KAFKA_PORT")}'
}


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def main():
    producer = Producer(conf)

    # Send message
    producer.produce('Posts', key='key', value='Hello, Kafka!', callback=delivery_report)
    producer.flush()  # Wait for all messages to be delivered


if __name__ == "__main__":
    main()
