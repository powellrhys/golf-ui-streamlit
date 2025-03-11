import streamlit as st
import json
import plotly.express as px
import pandas as pd

from functions.ui_components import (
    configure_page_config
)

configure_page_config()

number_of_shots = st.sidebar.selectbox(
    label='Number of shot evaluate',
    options=[10, 20, 30, 40, 50, 100]
)

dist_metric = st.sidebar.selectbox(
    label='Club Distribution Metric',
    options=[
        'Carry',
        'Distance'
    ]
)

min_stats = st.sidebar.checkbox(
    label='Minimum Statistics',
    value=False
)

max_stats = st.sidebar.checkbox(
    label='Maximum Statistics',
    value=False
)

avg_stats = st.sidebar.checkbox(
    label='Average Statistics',
    value=True
)

# Read the JSON file
with open(f'data/yardage_summary/latest_{number_of_shots}_shot_summary.json', 'r') as json_file:
    data = json.load(json_file)

df = pd.DataFrame([{"Club": list(d.keys())[0], **list(d.values())[0]} for d in data])

st.title('Trackman Yardages')

with st.expander(label='Yardage Table',
                 expanded=True):

    col_mapping = {
        column: column.replace('_', ' ').upper()
        for column in df.columns
    }

    filters = [word for word, flag in
               zip(["min", "max", "avg"], [min_stats, max_stats, avg_stats])
               if flag]
    filters = [col for col in df.columns if any(f in col for f in filters)]
    filters.insert(0, 'Club')

    yardage_df = df[filters]

    st.dataframe(data=yardage_df.rename(columns=col_mapping),
                 hide_index=True)

with st.expander(label='Club Distribution',
                 expanded=True):

    df_long = df.melt(id_vars=["Club"],
                      value_vars=[f"min_{dist_metric.lower()}",
                                  f"max_{dist_metric.lower()}"],
                      var_name=dist_metric.lower(),
                      value_name=dist_metric)

    df_long = df_long.sort_values(by=dist_metric,
                                  ascending=True)

    # Step 1: Get the average carry distances from the original df
    club_order = df.sort_values(by=f"avg_{dist_metric.lower()}",
                                ascending=True)["Club"]

    # Step 2: Apply this order to the long dataframe
    df_long["Club"] = pd.Categorical(df_long["Club"],
                                     categories=club_order,
                                     ordered=True)

    # Step 3: Sort df_long to ensure order is applied
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
