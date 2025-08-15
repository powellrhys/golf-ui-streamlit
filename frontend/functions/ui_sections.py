# Import dependencies
from shared import Variables, BlobClient
from .ui_components import display_club_metrics
from .data_functions import (
    collect_yardage_summary_data,
    collect_club_trajectory_data,
    extract_stat_flags
)
import streamlit as st

from functions.plots import (
    plot_final_trajectory_contour,
    plot_shot_trajectories
)
from functions.plots import (
    plot_club_distribution_stats
)

def render_trackman_club_analysis(variables: Variables) -> None:
    """
    """
    # Define page title
    st.title('Trackman Club Analysis')

    columns = st.columns([2, 1, 2])

    blob_files = BlobClient().list_blob_filenames(container_name="golf", directory_path="trackman_club_summary")
    clubs = [f.replace('.json', '').split("/")[-1] for f in blob_files]

    # Render select box within first column
    with columns[0]:
        club = st.selectbox(label="Club", options=clubs)

    # Render total shots slider in final column
    with columns[-1]:
        total_shots = st.slider(label="Most recent shots:", min_value=0, max_value=30, value=10)

    # Collect page data
    final_flight_df, final_end_df, carry_data, total_distance, ball_speeds = \
        collect_club_trajectory_data(
            club=club,
            total_shots=total_shots
        )

    # Render club metric boxes
    display_club_metrics(total_shots=total_shots,
                         carry_data=carry_data,
                         total_distance=total_distance,
                         ball_speeds=ball_speeds)

    # Define shot trajectory expander
    with st.expander(label='Shot Trajectory', expanded=True):

        # Plot all trajectories using Plotly Express
        plot_shot_trajectories(df=final_flight_df)

    # Define shot distribution expander
    with st.expander(label='Shot Distribution', expanded=True):

        # Generate plotly go contour plot
        plot_final_trajectory_contour(df=final_end_df)

def render_club_yardage_analysis() -> None:
    """
    """
    columns = st.columns([1, 1, 1])

    with columns[1]:
        # Define number of shots select box
        number_of_shots = st.selectbox(
            label='Number of shot to evaluate',
            options=[10, 20, 30, 40, 50, 100]
        )

    with columns[2]:
        # Define metric select box
        dist_metric = st.selectbox(
            label='Club Distribution Metric',
            options=['Carry', 'Distance']
        )
    with columns[0]:
        options = ["Min Stats", "Max Stats", "Avg Stats"]
        metrics = st.segmented_control(
            label="Display Stats", options=options, selection_mode="multi", default="Avg Stats"
        )

    min_stats, max_stats, avg_stats = extract_stat_flags(metrics)

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
