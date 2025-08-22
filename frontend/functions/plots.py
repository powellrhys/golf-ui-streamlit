# Import python packages
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

def plot_final_trajectory_contour(
    df: pd.DataFrame
) -> None:
    """
    Plots a 2D contour plot of the final shot trajectory using Plotly.

    This function creates a contour plot based on the x and z coordinates from
    a DataFrame and overlays a scatter plot of individual points on top of the
    contour. The contour plot represents the density of points, and the scatter
    plot highlights specific shot positions. The resulting plot is displayed
    in a Streamlit app.

    Args:
        df (pd.DataFrame): A DataFrame containing shot data with 'x' and 'z'
                           columns representing the coordinates of the shots.

    Returns:
        None: This function does not return any value. It displays the plot in
              a Streamlit application.
    """
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
