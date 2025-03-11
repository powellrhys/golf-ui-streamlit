# Import python packages
import plotly.express as px
import streamlit as st
import pandas as pd
import json

# Import project functions
from functions.ui_components import (
    configure_page_config
)

# Configure page config
configure_page_config()

# Define number of shots select box
number_of_shots = st.sidebar.selectbox(
    label='Number of shot evaluate',
    options=[10, 20, 30, 40, 50, 100]
)

# define metric select box
dist_metric = st.sidebar.selectbox(
    label='Club Distribution Metric',
    options=[
        'Carry',
        'Distance'
    ]
)

# Define min stats checkbox
min_stats = st.sidebar.checkbox(
    label='Minimum Statistics',
    value=False
)

# Define max stats checkbox
max_stats = st.sidebar.checkbox(
    label='Maximum Statistics',
    value=False
)

# Define avg stats checkbox
avg_stats = st.sidebar.checkbox(
    label='Average Statistics',
    value=True
)

# Read the JSON file
with open(f'data/yardage_summary/latest_{number_of_shots}_shot_summary.json', 'r') as json_file:
    data = json.load(json_file)

# Generate dataframe from json data read in
df = pd.DataFrame([{"Club": list(d.keys())[0], **list(d.values())[0]} for d in data])

# Render page title
st.title('Trackman Yardages')

# Render Yardage table expander
with st.expander(label='Yardage Table',
                 expanded=True):

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

    # Render yardage table
    st.dataframe(data=yardage_df.rename(columns=col_mapping),
                 hide_index=True)

# Render club distribution expander
with st.expander(label='Club Distribution',
                 expanded=True):

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

    # Create the box plot
    fig = px.line(df_long,
                  x="Club",
                  y=dist_metric,
                  color="Club",
                  markers='o',
                  )
    fig.update_layout(yaxis_title=f'{dist_metric} (m)')

    # Display in Streamlit
    st.plotly_chart(fig)
