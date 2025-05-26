import os

from confluent_kafka import Consumer
from dotenv import load_dotenv

load_dotenv()

# Configure consumer
conf = {
    'bootstrap.servers': f'{os.getenv("KAFKA_HOST")}:{os.getenv("KAFKA_PORT")}',
    'group.id': 'python-group',
    'auto.offset.reset': 'earliest'  # or 'latest'
}


def main():
    consumer = Consumer(conf)
    # Subscribe to topic(s)
    consumer.subscribe(['Posts', 'dbserver1.public.posts', 'dbserver1.public.users', 'dbserver1.public.comments'])

    print("Consuming messages from 'Posts'...")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)  # Poll for a message
            if msg is None:
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue
            print(f"Received message: {msg.value().decode('utf-8')}")

    except KeyboardInterrupt:
        pass
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()


if __name__ == "__main__":
    main()
