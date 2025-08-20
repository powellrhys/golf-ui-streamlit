# Import dependencies
import streamlit as st

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
