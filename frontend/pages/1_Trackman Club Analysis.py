# Import python packages
import streamlit as st
import os

# Import ui functions
from functions.ui_components import (
    configure_page_config,
    display_club_metrics
)

# Import logging functions
from functions.logging_functions import (
    log_input_change,
    log_page_change
)

# Import custom figures
from functions.plots import (
    plot_final_trajectory_contour,
    plot_shot_trajectories
)

# Import data functions
from functions.data_functions import (
    collect_club_trajectory_data,
    ProjectVariables
)

# Configure page config
logger = configure_page_config()

# Collect current page name
current_page = os.path.basename(__file__).split('_')[-1].replace('.py', '')

# Log page change
logger = log_page_change(logger=logger,
                         current_page=current_page)

# Collect all project variables
variables = ProjectVariables()

# Define sidebar club select box
club = st.sidebar.selectbox(
    label="Club",
    options=variables.clubs,
    key='p1_club_selectbox',
    on_change=log_input_change(
        logger=logger,
        msg_func=lambda: f'Club selection select box changed to {st.session_state.p1_club_selectbox}',
    )
)

# Define total shots slider
total_shots = st.sidebar.slider(
    label="Most recent shots:",
    min_value=0,
    max_value=30,
    value=variables.initial_shot_slider,
    key='p1_total_shots_slider',
    on_change=log_input_change(
        logger=logger,
        msg_func=lambda: f'Number of shots slider changed to {st.session_state.p1_total_shots_slider}'
    )
)

final_flight_df, final_end_df, carry_data, total_distance, ball_speeds = \
    collect_club_trajectory_data(
        club=club,
        total_shots=total_shots
    )

# Define page title
st.title('Trackman Club Analysis')

# Render club metric boxes
display_club_metrics(total_shots=total_shots,
                     carry_data=carry_data,
                     total_distance=total_distance,
                     ball_speeds=ball_speeds)

# Define shot trajectory expander
with st.expander(label='Shot Trajectory',
                 expanded=True):

    # Plot all trajectories using Plotly Express
    plot_shot_trajectories(df=final_flight_df)

# Define shot distribution expander
with st.expander(label='Shot Distribution',
                 expanded=True):

    # Generate plotly go contour plot
    plot_final_trajectory_contour(df=final_end_df)
