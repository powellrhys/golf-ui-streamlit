import streamlit as st
import pandas as pd
import json
import os

class ProjectVariables:

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
    '''
    '''
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
    '''
    '''
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
