# Import dependencies
from .ui_components import display_club_metrics
from shared import BlobClient
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

def render_trackman_club_analysis() -> None:
    """
    Render an interactive Streamlit dashboard for analyzing TrackMan club data.

    This function generates a web interface that allows the user to:
        - Select a golf club from available TrackMan session data.
        - Adjust the number of most recent shots to analyze.
        - View key metrics for the selected club (carry distance, total distance, ball speed, etc.).
        - Visualize shot trajectories and shot distributions using interactive plots.

    The function fetches TrackMan data from Azure Blob Storage, processes it using
    `collect_club_trajectory_data`, and renders visualizations with Plotly and Streamlit.

    User Interface Components:
        - Club selection dropdown.
        - Slider to select the number of most recent shots.
        - Metric boxes showing aggregated statistics.
        - Expandable sections for:
            - Shot trajectories.
            - Shot distribution contours.

    Returns:
        None
    """
    # Define page title
    st.title('Trackman Club Analysis')

    # Define columns object
    columns = st.columns([2, 1, 2])

    # Collect a list of clubs used on the trackman range
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
    Render an interactive Streamlit dashboard for analyzing TrackMan club yardage data.

    This function provides a web interface that allows users to:
        - Select which statistics to display (Minimum, Maximum, Average) for club shots.
        - Choose the number of most recent shots to include in the analysis.
        - Select the distribution metric to visualize (Carry or Total Distance).

    The function processes TrackMan yardage summary data by:
        - Extracting the selected statistics flags using `extract_stat_flags`.
        - Collecting and transforming club yardage data via `collect_yardage_summary_data`.

    User Interface Components:
        - Segmented control for selecting stats to display (Min, Max, Avg).
        - Dropdown for choosing the number of shots to evaluate.
        - Dropdown for selecting the club distribution metric.
        - Expandable section displaying a table of yardage statistics.
        - Expandable section displaying plots of club distribution based on the selected metric.

    Returns:
        None
    """
    # Define column object
    columns = st.columns([1, 1, 1])

    # Render the display stats segment control object in the first column
    with columns[0]:
        options = ["Min Stats", "Max Stats", "Avg Stats"]
        metrics = st.segmented_control(
            label="Display Stats", options=options, selection_mode="multi", default="Avg Stats"
        )

    # Render number of shots select box within the middle column
    with columns[1]:
        number_of_shots = st.selectbox(
            label='Number of shot to evaluate',
            options=[10, 20, 30, 40, 50, 100]
        )

    # Render the distribution metric in the final column
    with columns[2]:
        dist_metric = st.selectbox(
            label='Club Distribution Metric',
            options=['Carry', 'Distance']
        )

    # Collect boolean matrix of stats to render
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
