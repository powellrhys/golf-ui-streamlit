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
    """
    Configures the Streamlit page settings and initializes logging.

    This function sets up the page configuration, including the sidebar state,
    layout, and page icon. It also suppresses warnings, configures logging,
    and checks if the Kafka logging server is running.

    Args:
        initial_sidebar_state (str, optional): The initial state of the sidebar
                                               ("expanded" or "collapsed").
                                               Defaults to "expanded".
        layout (str, optional): The layout of the page ("wide" or "centered").
                                Defaults to "wide".
        page_icon (str, optional): The icon to display in the browser tab.
                                   Defaults to ":golf:".

    Returns:
        logging.Logger: The configured logger instance.
    """
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
    """
    Displays key club performance metrics in a Streamlit app.

    This function calculates and displays the average carry, average total
    distance, and average ball speed from the last `total_shots` using Streamlit
    metrics. Each metric is shown in a separate column on the page.

    Args:
        total_shots (int): The total number of shots considered for calculating
                            the averages.
        carry_data (list): A list of carry distances for each shot.
        total_distance (list): A list of total distances for each shot.
        ball_speeds (list): A list of ball speeds for each shot.

    Returns:
        None: This function does not return any value. It displays the metrics
              in a Streamlit application.
    """
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
    """
    Checks if the Kafka and Zookeeper containers are running.

    This function verifies if both the Zookeeper and Kafka containers are
    running. If either of them is not running, a warning message is displayed
    in the Streamlit app, indicating that logs will not be stored due to the
    Kafka server being unavailable.

    Args:
        logger (logging.Logger): The logger instance used to log any issues or
                                  warnings related to the server status.

    Returns:
        None: This function does not return any value. It displays a warning
              in the Streamlit app if the Kafka server is not running.
    """
    # Check if zookeeper and kafka containers are running
    if not is_container_running(container_name='zookeeper',
                                logger=logger):
        if not is_container_running(container_name='kafka',
                                    logger=logger):
            st.warning('Logs will not be stored - kafka server not running')
