# Import python packages
import streamlit as st
import pandas as pd
import json
import os


class Variables:
    """
    """
    def __init__(self):
        # Define list of clubs
        self.clubs_directory = "data/club_summary/"
        self.clubs = [f.replace('.json', '')
                      for f in os.listdir(self.clubs_directory)
                      if os.path.isfile(os.path.join(self.clubs_directory, f))]

def extract_stat_flags(metrics):
    """
    """
    min_stats = "Min Stats" in metrics
    max_stats = "Max Stats" in metrics
    avg_stats = "Avg Stats" in metrics

    return min_stats, max_stats, avg_stats

class ProjectVariables:
    """
    A class to manage project-specific variables and Streamlit session state initialization.

    This class initializes and maintains essential variables for the application, including:
    - A list of available clubs derived from JSON files in a specified directory.
    - Default values for various shot-related sliders.
    - Initialization of Streamlit session state variables to ensure consistent application behavior.

    Attributes:
        clubs_directory (str): Directory path containing club summary JSON files.
        clubs (list): List of club names derived from JSON filenames.
        initial_shot_slider (int): Default value for shot-related sliders.

    Session State Variables:
        p1_club_selectbox (str): Selected club for player 1.
        p1_total_shots_slider (int): Number of total shots for player 1.
        p3_number_of_shots_selectbox (int): Number of shots for player 3.
        p3_dist_metric_selectbox (str): Distance metric for player 3 (default: 'Carry').
        p3_min_stats_checkbox (bool): Checkbox state for minimum stats display.
        p3_max_stats_checkbox (bool): Checkbox state for maximum stats display.
        p3_avg_stats_checkbox (bool): Checkbox state for average stats display.
    """
    def __init__(self):

        # Define list of clubs
        self.clubs_directory = "data/club_summary/"
        self.clubs = [f.replace('.json', '')
                      for f in os.listdir(self.clubs_directory)
                      if os.path.isfile(os.path.join(self.clubs_directory, f))]

        # Define initial state of all shot sliders
        self.initial_shot_slider = 10

        # Ensure the p1_club_selectbox session state variable is initialized
        if "p1_club_selectbox" not in st.session_state:
            st.session_state.p1_club_selectbox = self.clubs[0]

        # Ensure the p1_total_shots_slider session state variable is initialized
        if "p1_total_shots_slider" not in st.session_state:
            st.session_state.p1_total_shots_slider = self.initial_shot_slider

        # Ensure the p3_number_of_shots_selectbox session state variable is initialized
        if "p3_number_of_shots_selectbox" not in st.session_state:
            st.session_state.p3_number_of_shots_selectbox = self.initial_shot_slider

        # Ensure the p3_number_of_shots_selectbox session state variable is initialized
        if "p3_dist_metric_selectbox" not in st.session_state:
            st.session_state.p3_dist_metric_selectbox = 'Carry'

        # Ensure the p3_min_stats_checkbox session state variable is initialized
        if "p3_min_stats_checkbox" not in st.session_state:
            st.session_state.p3_min_stats_checkbox = False

        # Ensure the p3_max_stats_checkbox session state variable is initialized
        if "p3_max_stats_checkbox" not in st.session_state:
            st.session_state.p3_max_stats_checkbox = False

        # Ensure the p3_avg_stats_checkbox session state variable is initialized
        if "p3_avg_stats_checkbox" not in st.session_state:
            st.session_state.p3_avg_stats_checkbox = True


def collect_club_trajectory_data(
    club: str,
    total_shots: int
) -> tuple[pd.DataFrame,
           pd.DataFrame,
           list,
           list,
           list]:
    """
    Collects and processes trajectory data for a specified golf club.

    This function reads shot data from a JSON file corresponding to the given club and
    extracts relevant trajectory and performance metrics for a specified number of shots.

    Args:
        club (str): The name of the club for which trajectory data is collected.
        total_shots (int): The number of shots to process from the dataset.

    Returns:
        tuple: A tuple containing:
            - pd.DataFrame: A DataFrame with trajectory data for all shots.
            - pd.DataFrame: A DataFrame containing final position data for each shot.
            - list: A list of carry distances for each shot.
            - list: A list of total distances for each shot.
            - list: A list of ball speeds for each shot.

    The function processes each shot by extracting:
        - Carry, total distance, and ball speed from the measurement data.
        - Adjusted (x, y, z) coordinates for the ball's trajectory.
        - The final position of each shot.

    The trajectory data is stored in Pandas DataFrames, and other metrics are returned as lists.
    """
    # Read the JSON file
    with open(f'data/club_summary/{club}.json', 'r') as json_file:
        data = json.load(json_file)

    # Define empty stat arrays
    all_data = []
    end_data = []
    carry_data = []
    total_distance = []
    ball_speeds = []

    # Iterate through data and collect stats
    for idx, data_set in enumerate(data[0:total_shots]):

        # Collect and append stroke stat
        carry_data.append(data_set['Measurement']['Carry'])
        total_distance.append(data_set['Measurement']['Total'])
        ball_speeds.append(data_set['Measurement']['BallSpeed'])

        # Cllect initial and final shot data
        x_initial = data_set['Measurement']['BallTrajectory'][0]['X']
        z_initial = data_set['Measurement']['BallTrajectory'][0]['Z']
        y_low = min([point['Y']
                    for point in data_set['Measurement']['BallTrajectory']])

        # Collect trajectory data
        x_data = [point['X'] - x_initial
                  for point in data_set['Measurement']['BallTrajectory']]
        y_data = [point['Y'] - y_low
                  for point in data_set['Measurement']['BallTrajectory']]
        z_data = [point['Z'] - z_initial
                  for point in data_set['Measurement']['BallTrajectory']]

        # Collect final state of each shot
        x_end = x_data[-1]
        z_end = z_data[-1]

        # Create a DataFrame for each trajectory with an identifier
        df_flight = pd.DataFrame({
            'x': x_data,
            'y': y_data,
            'Shot': f'Shot {idx + 1}'
        })

        # Append flight data to all data array
        all_data.append(df_flight)

        # Define end state dataframe
        df_end = pd.DataFrame({
            'x': [x_end],
            'z': [z_end],
            'Shot': [f'Shot {idx + 1}']
        })

        # Append end state dataframe to array
        end_data.append(df_end)

    # Concatenate all data into a single DataFrame
    final_flight_df = pd.concat(all_data, ignore_index=True)
    final_end_df = pd.concat(end_data, ignore_index=True)

    return final_flight_df, final_end_df, carry_data, total_distance, ball_speeds


def collect_yardage_summary_data(
    number_of_shots: int,
    min_stats: bool,
    max_stats: bool,
    avg_stats: bool,
    dist_metric: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Collects and processes yardage summary data for a specified number of shots.

    This function reads yardage summary data from a JSON file and processes it into
    two Pandas DataFrames: one summarizing selected statistics and another formatted
    for visualization.

    Args:
        number_of_shots (int): The number of shots to retrieve data for.
        min_stats (bool): Whether to include minimum yardage statistics.
        max_stats (bool): Whether to include maximum yardage statistics.
        avg_stats (bool): Whether to include average yardage statistics.
        dist_metric (str): The distance metric to be used (e.g., "Carry", "Total").

    Returns:
        tuple:
            - pd.DataFrame: A DataFrame containing yardage summary statistics based on selected filters.
            - pd.DataFrame: A long-format DataFrame suitable for visualization, sorted by club and distance.

    The function performs the following operations:
        - Reads shot summary data from a JSON file.
        - Creates a DataFrame with club names and corresponding statistics.
        - Filters columns based on the selected statistics (min, max, avg).
        - Renames columns for better readability.
        - Converts the DataFrame into a long format for visualization.
        - Sorts data by the specified distance metric.
    """
    # Read the JSON file
    with open(f'data/yardage_summary/latest_{number_of_shots}_shot_summary.json', 'r') as json_file:
        data = json.load(json_file)

    # Generate dataframe from json data read in
    df = pd.DataFrame([{"Club": list(d.keys())[0], **list(d.values())[0]} for d in data])

    # Map column headers to better formatted titles
    col_mapping = {
        column: column.replace('_', ' ').upper()
        for column in df.columns
    }

    # Identify which columns to render
    filters = [word for word, flag in
               zip(["min", "max", "avg"], [min_stats, max_stats, avg_stats])
               if flag]

    # Identify which columns to render
    filters = [col for col in df.columns if any(f in col for f in filters)]
    filters.insert(0, 'Club')

    # Generate yardage summary dataframe
    yardage_df = df[filters]

    # Rename all columns based on column mapping
    yardage_df.rename(columns=col_mapping)

    # Turn dataframe into long format
    df_long = df.melt(id_vars=["Club"],
                      value_vars=[f"min_{dist_metric.lower()}",
                                  f"max_{dist_metric.lower()}"],
                      var_name=dist_metric.lower(),
                      value_name=dist_metric)

    # Sort values
    df_long = df_long.sort_values(by=dist_metric,
                                  ascending=True)

    # Get the average carry distances from the original df
    club_order = df.sort_values(by=f"avg_{dist_metric.lower()}",
                                ascending=True)["Club"]

    # Apply this order to the long dataframe
    df_long["Club"] = pd.Categorical(df_long["Club"],
                                     categories=club_order,
                                     ordered=True)

    # Sort df_long to ensure order is applied
    df_long = df_long.sort_values(by="Club")

    return yardage_df, df_long
