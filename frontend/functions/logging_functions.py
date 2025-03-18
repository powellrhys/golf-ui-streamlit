# Import python packages
from confluent_kafka import Producer
from docker.errors import NotFound
from typing import Callable
import streamlit as st
import datetime
import logging
import docker


class KafkaLoggingHandler(logging.Handler):
    """
    A logging handler that sends log messages to an Apache Kafka topic.

    This handler extends `logging.Handler` and publishes formatted log records
    to a specified Kafka topic using the `confluent_kafka.Producer`.

    Attributes:
        producer (confluent_kafka.Producer): The Kafka producer instance.
        topic (str): The Kafka topic where log messages will be sent.

    Args:
        kafka_broker (str): The Kafka broker address (e.g., "localhost:9092").
        topic (str): The Kafka topic to which log messages should be published.

    Methods:
        emit(record): Formats and sends a log record to the Kafka topic.
    """
    def __init__(self, kafka_broker, topic):
        super().__init__()
        self.producer = Producer({'bootstrap.servers': kafka_broker})
        self.topic = topic

    def emit(self, record):
        try:
            log_entry = self.format(record)
            self.producer.produce(self.topic, log_entry.encode('utf-8'))
            self.producer.flush()
        except Exception as e:
            print(f"Error sending log to Kafka: {e}")


def configure_logging() -> logging.Logger:
    """
    Configures and returns a logger for the Streamlit application.

    This function sets up a logger named "streamlit_app" with two handlers:
    1. A `StreamHandler` that outputs logs to the console.
    2. A `KafkaLoggingHandler` that sends logs to a Kafka topic.

    If the logger already has handlers, it will not add duplicates.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger("streamlit_app")

    if not logger.hasHandlers():
        # Console Handler
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # Kafka Handler
        kafka_handler = KafkaLoggingHandler(kafka_broker='localhost:9092', topic='streamlit_logs')
        kafka_handler.setFormatter(formatter)
        logger.addHandler(kafka_handler)

        logger.setLevel(logging.INFO)

    return logger


def log_page_change(
    logger: logging.Logger,
    current_page: str
) -> logging.Logger:
    """
    Logs page navigation events in a Streamlit application.

    This function checks if the user has navigated to a new page and logs the
    time spent on the previous page before recording the visit to the new page.

    Args:
        logger (logging.Logger): The logger instance used for logging.
        current_page (str): The name of the current page the user is visiting.

    Returns:
        logging.Logger: The logger instance.
    """
    # Check if the page has changed
    if "last_page" not in st.session_state or st.session_state.last_page != current_page:

        if 'page_change_time' in st.session_state:
            logger.info(f'Time spent on the {st.session_state.last_page} page: '
                        f'{datetime.datetime.now() - st.session_state.page_change_time} \n')

        logger.info(f'{current_page} Page visited')

        st.session_state.last_page = current_page
        st.session_state.page_change_time = datetime.datetime.now()

    return logger


def log_input_change(
    logger: logging.Logger,
    msg_func: Callable[[], str]
) -> Callable[[], str]:
    """
    Logs input changes by wrapping a callback function.

    This function takes a logger and a message-generating function, then returns
    a new callback function that logs the output of `msg_func` when executed.

    Args:
        logger (logging.Logger): The logger instance used to log the messages.
        msg_func (Callable[[], str]): A function that returns a string message to be logged.

    Returns:
        Callable[[], str]: A callback function that logs the result of `msg_func`.
    """
    def callback():
        # Log out message
        logger.info(msg_func())

    return callback


def is_container_running(
    container_name: str,
    logger: logging.Logger
) -> bool:
    """
    Checks if a Docker container is currently running.

    This function uses the Docker client to retrieve a container by its name
    and checks its status. If the container is running, it returns True;
    otherwise, it returns False. It logs warnings if the container is not
    found or if an error occurs.

    Args:
        container_name (str): The name of the Docker container to check.
        logger (logging.Logger): The logger instance used to log warnings and errors.

    Returns:
        bool: True if the container is running, False otherwise.
    """
    # Collect docker client
    client = docker.from_env()

    try:
        # Get container by name
        container = client.containers.get(container_name)

        # Check if the container is running
        if container.status == 'running':
            return True
        else:
            return False
    except NotFound:
        logger.warning(f"Container '{container_name}' not found.")
        return False
    except Exception as e:
        logger.warning(f"An error occurred: {e}")
        return False
