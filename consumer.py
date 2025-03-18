# Import python packages
from confluent_kafka import (
    Consumer,
    KafkaException
)
import logging

# Create a logger specifically for Kafka logs
kafka_logger = logging.getLogger("kafka_logs")
kafka_logger.setLevel(logging.INFO)

# Create a file handler without a formatter (to avoid duplicate timestamps)
file_handler = logging.FileHandler("data/logs/application_logs.log")
file_handler.setFormatter(None)
kafka_logger.addHandler(file_handler)

# Prevent logs from being duplicated to root logger
kafka_logger.propagate = False

# Kafka configuration
conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'log-consumer-group',
    'auto.offset.reset': 'earliest',
}

# Configure consumer and subscribe to streaming topic
consumer = Consumer(conf)
topic = "streamlit_logs"
consumer.subscribe([topic])

# Poll kafka stream for entries
try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            logging.error(f"Kafka error: {msg.error()}")
            raise KafkaException(msg.error())

        # Log Kafka messages exactly as they appear, without "INFO:root:"
        kafka_logger.info(msg.value().decode("utf-8").strip())

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
