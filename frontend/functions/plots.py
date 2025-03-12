# Import python packages
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd

def plot_shot_trajectories(
    df: pd.DataFrame
) -> None:
    '''
    '''
    # Plot all trajectories using Plotly Express
    fig = px.line(data_frame=df,
                  x='x',
                  y='y',
                  color='Shot',
                  )
    fig.update_layout(yaxis_title="Height (m)")
    fig.update_layout(xaxis_title="Distance (m)")

    # Display in Streamlit
    st.plotly_chart(fig)


def plot_final_trajectory_contour(
    df: pd.DataFrame
) -> None:
    '''
    '''
    # Generate plotly go contour plot
    fig = go.Figure(
        go.Histogram2dContour(
            x=df['z'],
            y=df['x'],
            colorscale='Blues',
        ))

    # Overlay static scatter data to contour plot
    fig.add_trace(go.Scatter(
        x=df['z'],
        y=df['x'],
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


def plot_club_distribution_stats(
    df: pd.DataFrame,
    dist_metric: str
) -> None:
    '''
    '''
    # Create the box plot
    fig = px.line(data_frame=df,
                  x="Club",
                  y=dist_metric,
                  color="Club",
                  markers='o',
                  )
    fig.update_layout(yaxis_title=f'{dist_metric} (m)')

    # Display in Streamlit
    st.plotly_chart(fig)
