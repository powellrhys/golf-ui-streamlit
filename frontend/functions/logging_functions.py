# Import python packages
from confluent_kafka import Producer
from typing import Callable
import streamlit as st
import datetime
import logging


class KafkaLoggingHandler(logging.Handler):
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
    '''
    '''
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
    '''
    '''
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
    '''
    '''
    def callback():
        '''
        '''
        # Log out message
        logger.info(msg_func())

    return callback
