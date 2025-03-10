import streamlit as st
import plotly.express as px
import os
import json
import pandas as pd

from functions.ui_components import (
    configure_page_config
)

configure_page_config()

# Specify the directory path
directory = "data/club_summary/"

# List all files in the directory
clubs = [f.replace('.json', '')
         for f in os.listdir(directory)
         if os.path.isfile(os.path.join(directory, f))]

club = st.sidebar.selectbox(
    "Club",
    clubs,
)

total_shots = st.sidebar.slider(label="Most recent shots:",
                                min_value=0,
                                max_value=30,
                                value=10)

# Read the JSON file
with open(f'{directory}/{club}.json', 'r') as json_file:
    data = json.load(json_file)

all_data = []  # List to store data from all data_sets
end_data = []
carry_data = []
total_distance = []
ball_speeds = []

for idx, data_set in enumerate(data[0:total_shots]):

    carry_data.append(data_set['Measurement']['Carry'])
    total_distance.append(data_set['Measurement']['Total'])
    ball_speeds.append(data_set['Measurement']['BallSpeed'])

    x_initial = data_set['Measurement']['BallTrajectory'][0]['X']
    z_initial = data_set['Measurement']['BallTrajectory'][0]['Z']
    y_low = min([point['Y'] 
                 for point in data_set['Measurement']['BallTrajectory']])

    x_data = [point['X'] - x_initial
              for point in data_set['Measurement']['BallTrajectory']]
    y_data = [point['Y'] - y_low
              for point in data_set['Measurement']['BallTrajectory']]
    z_data = [point['Z'] - z_initial
              for point in data_set['Measurement']['BallTrajectory']]

    x_end = x_data[-1]
    z_end = z_data[-1]

    # Create a DataFrame for each trajectory with an identifier
    df_flight = pd.DataFrame({
        'x': x_data,
        'y': y_data,
        'Shot': f'Shot {idx + 1}'  # Label for each trajectory
    })

    all_data.append(df_flight)  # Append to list

    df_end = pd.DataFrame({
        'x': [x_end],
        'z': [z_end],
        'Shot': [f'Shot {idx + 1}']
    })

    end_data.append(df_end)

st.title('Trackman Club Analysis')

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(label=f'Average Carry  (Last {total_shots} shots)',
              value=f'{round(sum(carry_data)/len(carry_data), 2)}m',
              border=True)

with col2:

    st.metric(label=f'Average Distance (Last {total_shots} shots)',
              value=f'{round(sum(total_distance)/len(total_distance), 2)}m',
              border=True)

with col3:

    st.metric(label=f'Avg Ball Speed  (Last {total_shots} shots)',
              value=f'{round(sum(ball_speeds)/len(ball_speeds), 2)}mph',
              border=True)

# Concatenate all data into a single DataFrame
final_flight_df = pd.concat(all_data, ignore_index=True)
final_end_df = pd.concat(end_data, ignore_index=True)

with st.expander('Shot Trajectory'):

    # Plot all trajectories using Plotly Express
    fig = px.line(data_frame=final_flight_df,
                  x='x',
                  y='y',
                  color='Shot',
                  )

    # Display in Streamlit
    st.plotly_chart(fig)

with st.expander('Shot Distribution'):

    import plotly.graph_objects as go

    fig = go.Figure(
        go.Histogram2dContour(
            x=final_end_df['z'],
            y=final_end_df['x'],
            colorscale='Blues',
        ))

    fig.add_trace(go.Scatter(
        x=final_end_df['z'],
        y=final_end_df['x'],
        xaxis='x',
        yaxis='y',
        mode='markers',
        marker=dict(
            color='black',
            size=8
        )
    ))

    # Display in Streamlit
    st.plotly_chart(fig)
