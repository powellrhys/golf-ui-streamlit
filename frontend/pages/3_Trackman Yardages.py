# Import python packages
import streamlit as st
import os

# Import ui functions
from functions.ui_components import (
    configure_page_config
)

# Import logging functions
from functions.logging_functions import (
    log_input_change,
    log_page_change
)

# Import data functions
from functions.data_functions import (
    collect_yardage_summary_data,
    ProjectVariables
)

# Import figure functions
from functions.plots import (
    plot_club_distribution_stats
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

# Define number of shots select box
number_of_shots = st.sidebar.selectbox(
    label='Number of shot to evaluate',
    options=[10, 20, 30, 40, 50, 100],
    key='p3_number_of_shots_selectbox',
    on_change=log_input_change(
        logger=logger,
        msg_func=lambda: f'Number of shots select box changed to {st.session_state.p3_number_of_shots_selectbox}'
    )
)

# Define metric select box
dist_metric = st.sidebar.selectbox(
    label='Club Distribution Metric',
    options=['Carry', 'Distance'],
    key='p3_dist_metric_selectbox',
    on_change=log_input_change(
        logger=logger,
        msg_func=lambda: f'Club distribution metric changed to {st.session_state.p3_dist_metric_selectbox}'
    )
)

# Define min stats checkbox
min_stats = st.sidebar.checkbox(
    label='Minimum Statistics',
    value=False,
    key='p3_min_stats_checkbox',
    on_change=log_input_change(
        logger=logger,
        msg_func=lambda: f'Display minimum stats toggle changed to {st.session_state.p3_min_stats_checkbox}'
    )
)

# Define max stats checkbox
max_stats = st.sidebar.checkbox(
    label='Maximum Statistics',
    value=False,
    key='p3_max_stats_checkbox',
    on_change=log_input_change(
        logger=logger,
        msg_func=lambda: f'Display maximum stats toggle changed to {st.session_state.p3_max_stats_checkbox}'
    )
)

# Define avg stats checkbox
avg_stats = st.sidebar.checkbox(
    label='Average Statistics',
    value=True,
    key='p3_avg_stats_checkbox',
    on_change=log_input_change(
        logger=logger,
        msg_func=lambda: f'Display average stats toggle changed to {st.session_state.p3_avg_stats_checkbox}'
    )
)

# Collect and transform club summary yardage data
yardage_df, df_long = \
    collect_yardage_summary_data(
        number_of_shots=number_of_shots,
        min_stats=min_stats,
        max_stats=max_stats,
        avg_stats=avg_stats,
        dist_metric=dist_metric
    )

# Render page title
st.title('Trackman Yardages')

# Render Yardage table expander
with st.expander(label='Yardage Table',
                 expanded=True):

    # Render yardage table
    st.dataframe(data=yardage_df,
                 hide_index=True)

# Render club distribution expander
with st.expander(label='Club Distribution',
                 expanded=True):

    # Plot distribution stats
    plot_club_distribution_stats(df=df_long,
                                 dist_metric=dist_metric)
