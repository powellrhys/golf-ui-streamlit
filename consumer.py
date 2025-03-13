from confluent_kafka import Consumer, KafkaException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Kafka configuration
conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'log-consumer-group',
    'auto.offset.reset': 'earliest'
}

# Create Kafka consumer
consumer = Consumer(conf)
topic = "streamlit_logs"

# Subscribe to the topic
consumer.subscribe([topic])

try:
    while True:
        msg = consumer.poll(1.0)  # Poll for messages
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())

        logging.info(f"Consumed: {msg.value().decode('utf-8')}")

except KeyboardInterrupt:
    logging.info("Consumer shutdown.")
finally:
    consumer.close()
