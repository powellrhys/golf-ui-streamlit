# Import dependencies
from .plots import plot_final_trajectory_contour, plot_strokes_per_hole, plot_fairways_hit
from streamlit_components.plot_functions import PlotlyPlotter
from .ui_components import display_club_metrics
from .data_functions import (
    transform_stroke_per_hole_data,
    collect_yardage_summary_data,
    collect_club_trajectory_data,
    aggregate_fairway_data,
    extract_stat_flags
)
from shared import BlobClient, Variables
import streamlit as st

def render_hole_metrics(vars: Variables) -> list[dict]:
    """
    Render hole-level performance metrics in a Streamlit dashboard.

    Displays interactive selectors for hole and number of rounds,
    retrieves aggregated hole data from blob storage, and shows
    metrics such as par, stroke index, average strokes, average putts,
    and GIR percentage.

    Args:
        vars (Variables): Object containing configuration variables
            (e.g., golf course name).

    Returns: list[dict]: List of round data dictionaries for the selected hole.
    """
    # Configure columns
    columns = st.columns([1, 2, 1])

    # Render hole select box within the first column
    with columns[0]:
        hole = st.selectbox(label="Hole",
                            options=[f"Hole: {i + 1}" for i in range(18)])

    # Render slider within the final column
    with columns[-1]:

        # Read all round data from blob storage
        all_rounds = BlobClient().list_blob_filenames(container_name="golf", directory_path="scorecards")

        # Determine how many round have been played
        home_rounds_count = len([round for round in all_rounds if vars.golf_course_name.lower() in round.lower()])

        # Render rounds slider
        rounds = st.slider(label="Last N Rounds",
                           min_value=10,
                           max_value=home_rounds_count,
                           value=10)

    # Define file name from input variables
    file_name = f"{vars.golf_course_name}_golf_course_hole_summary/{hole.lower().replace(': ', '_')}.json"

    # Read data from blob
    data = BlobClient().read_blob_to_dict(container="golf", input_filename=file_name)[0:rounds]

    # Collect number of shots per round
    shots = [int(stroke["Strokes"]) for stroke in data if str(stroke["Strokes"]).isdigit()]

    # Collect number of puts taken per round
    putts = [int(stroke["Putts"]) for stroke in data if str(stroke["Putts"]).isdigit()]

    # Generate green in regulation list
    gir = [is_gir["Gir"] for is_gir in data]

    # Create metrics dictionary to display on frontend
    hole_overview = {
        "Stroke Index": data[0]["S. index"],
        "Par": data[0]["Par"],
        "Average Strokes": float(f"{sum(shots)/len(shots):.2f}"),
        "Average Putts": float(f"{sum(putts)/len(putts):.2f}"),
        "GIR (%)": float(f"{(sum(gir) / len(gir)) * 100:.2f}")
    }

    # Define 5 metric columns
    columns = st.columns(5)

    # Loop through metric dictionary and render metrics in each column
    for ind, (label, value) in enumerate(hole_overview.items()):
        with columns[ind]:
            st.metric(label=label.capitalize(), value=value, border=True)

    return data

def render_course_hole_by_hole_section(variables: Variables) -> None:
    """
    Render a Streamlit dashboard section for hole-by-hole course analysis.

    Displays hole-level metrics, fairway accuracy (if not a par 3),
    and stroke performance charts using aggregated round data.

    Args:
        variables (Variables): Object containing configuration
            variables (e.g., golf course name).

    Returns: None
    """
    # Define page title
    st.title(f"{variables.golf_course_name.capitalize()} GC Analysis")

    # Render hole metrics section
    data = render_hole_metrics(vars=Variables())

    # If hole is not a par 3, render a fairways hit section
    if data[0]["Par"] != 3:

        # Render fairway accuracy expander
        with st.expander(label="Fairway Accuracy Overview", expanded=True):

            # Aggregate fairway data and generate figure
            fairway_df = aggregate_fairway_data(data)
            fig = plot_fairways_hit(fairway_df)

            # Plot figure
            st.plotly_chart(fig)

    # Render stroke performance expander
    with st.expander(label="Stroke Performance Overview", expanded=True):

        # Transform strokes taken data and generate figure
        strokes_df = transform_stroke_per_hole_data(data=data)
        fig = plot_strokes_per_hole(df=strokes_df)

        # Render figure
        st.plotly_chart(fig)

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

    Returns: None
    """
    # Define page title
    st.title('Trackman Club Analysis')

    # Define columns object
    columns = st.columns([2, 1, 2])

    # Collect a list of clubs used on the trackman range
    blob_files = BlobClient(source="frontend") \
        .list_blob_filenames(container_name="golf", directory_path="trackman_club_summary")
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

        # Plot trajectory data
        st.plotly_chart(PlotlyPlotter(
            df=final_flight_df,
            x='x',
            y='y',
            color='Shot',
            labels={'x': 'Horizontal Distance (m)',
                    'y': 'Vertical Distance (m)'}).plot_line())

    # Define shot distribution expander
    with st.expander(label='Shot Distribution', expanded=True):

        # Generate plotly go contour plot
        plot_final_trajectory_contour(df=final_end_df)

def render_trackman_session_analysis() -> None:
    """
    Render a Streamlit dashboard section for analyzing Trackman sessions.

    Allows users to select a session date and club, retrieves Trackman
    session data from blob storage, and prepares it for visualization.

    Args: None

    Returns: None
    """
    # Define page title
    st.title('Trackman Session Analysis')

    # Define columns object
    columns = st.columns([2, 2, 1])

    # Collect a list of clubs used on the trackman range
    blob_files = BlobClient(source="frontend") \
        .list_blob_filenames(container_name="golf", directory_path="trackman_session_summary")

    # Create sessions dictionary
    sessions = [{"date": f.replace('.json', '').split("/")[-1].split("-session-")[0], "file_name": f}
                for f in blob_files]

    # Render session date select box in the first column
    with columns[0]:
        session_date = st.selectbox(
            label='Trackman Session Date',
            options=[session['date'] for session in sessions]
        )

        # Define file name based on frontend inputs
        filename = [entry["file_name"] for entry in sessions if entry["date"] == session_date][0]

    # Read data from blob
    data = BlobClient(source="frontend").read_blob_to_dict(container="golf", input_filename=filename)["StrokeGroups"]

    # Render club select box within second column
    with columns[1]:
        club = st.selectbox(
            label='Trackman Session Date',
            options=list(set([shot["Club"] for shot in data]))
        )

    st.write(club)

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

        # Map column headers
        yardage_df.columns = yardage_df.columns.str.replace("_", " ").str.upper()
        yardage_df.columns = yardage_df.columns + " (m)"

        # Render yardage table
        st.dataframe(data=yardage_df,
                     hide_index=True)

    # Render club distribution expander
    with st.expander(label='Club Distribution',
                     expanded=True):

        # Plot club distribution stats
        st.plotly_chart(PlotlyPlotter(
            df=df_long,
            x="Club",
            y=dist_metric,
            color="Club",
            markers='o').plot_line())
