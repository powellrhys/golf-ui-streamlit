# Import python packages
import streamlit as st
import warnings
import logging

# Import logging functions
from functions.logging_functions import (
    is_container_running,
    configure_logging,
)


def configure_page_config(
    initial_sidebar_state: str = "expanded",
    layout: str = "wide",
    page_icon: str = ":golf:"
) -> None:
    '''
    '''
    # Set page config
    st.set_page_config(
        initial_sidebar_state=initial_sidebar_state,
        layout=layout,
        page_icon=page_icon
    )

    # Ignore all warnings
    warnings.filterwarnings("ignore")

    logger = configure_logging()

    # Check if kakfa logging server is running
    check_if_server_is_running(logger=logger)

    return logger


def display_club_metrics(
    total_shots: int,
    carry_data: list,
    total_distance: list,
    ball_speeds: list
) -> None:
    '''
    '''
    # Define page columns
    col1, col2, col3 = st.columns(3)

    # Render average carry metric in column 1
    with col1:
        st.metric(label=f'Average Carry  (Last {total_shots} shots)',
                  value=f'{round(sum(carry_data)/len(carry_data), 2)}m',
                  border=True)

    # Render average distance metric in column 2
    with col2:
        st.metric(label=f'Average Distance (Last {total_shots} shots)',
                  value=f'{round(sum(total_distance)/len(total_distance), 2)}m',
                  border=True)

    # Render average ball speed metric in column 3
    with col3:
        st.metric(label=f'Avg Ball Speed  (Last {total_shots} shots)',
                  value=f'{round(sum(ball_speeds)/len(ball_speeds), 2)}mph',
                  border=True)


def check_if_server_is_running(
    logger: logging.Logger
) -> None:
    '''
    '''
    # Check if zookeeper and kafka containers are running
    if not is_container_running(container_name='zookeeper',
                                logger=logger):
        if not is_container_running(container_name='kafka',
                                    logger=logger):
            st.warning('Logs will not be stored - kafka server not running')
