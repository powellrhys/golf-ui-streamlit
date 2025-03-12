# Import python packages
from typing import Callable
import streamlit as st
import datetime
import logging

def configure_logging() -> logging.Logger:
    '''
    '''
    # Configure Logger
    logger = logging.getLogger("streamlit_app")
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
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
