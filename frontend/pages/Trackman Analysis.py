import streamlit as st
import plotly.express as px
import os
import json
import pandas as pd

# Specify the directory path
directory = "data/club_summary/"

# List all files in the directory
clubs = [f.replace('.json', '') for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

tab1, tab2, tab3 = st.tabs(['Club Analysis', 'Session Analysis', 'Yardages'])

with tab1:

    club = st.sidebar.selectbox(
        "Club",
        clubs,
    )

    total_shots = st.sidebar.slider(label="Most recent shots:",
                        min_value=0,
                        max_value=20,
                        value=10)

    # Read the JSON file
    with open(f'{directory}/{club}.json', 'r') as json_file:
        data = json.load(json_file)

    all_data = []  # List to store data from all data_sets

    for idx, data_set in enumerate(data[0:total_shots]):  # Iterate over all data_sets
        x_initial = data_set['Measurement']['BallTrajectory'][0]['X']
        y_low = min([point['Y'] for point in data_set['Measurement']['BallTrajectory']])
        x_data = [point['X'] - x_initial for point in data_set['Measurement']['BallTrajectory']]
        y_data = [point['Y'] - y_low for point in data_set['Measurement']['BallTrajectory']]

        # Create a DataFrame for each trajectory with an identifier
        df = pd.DataFrame({
            'x': x_data,
            'y': y_data,
            'Shot': f'Shot {idx + 1}'  # Label for each trajectory
        })

        all_data.append(df)  # Append to list

    # Concatenate all data into a single DataFrame
    final_df = pd.concat(all_data, ignore_index=True)

    # Plot all trajectories using Plotly Express
    fig = px.line(final_df, x='x', y='y', color='Shot', title="Multiple Ball Trajectories")

    # Display in Streamlit
    st.plotly_chart(fig)
