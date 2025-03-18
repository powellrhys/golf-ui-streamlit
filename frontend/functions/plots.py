# Import python packages
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd


def plot_shot_trajectories(
    df: pd.DataFrame
) -> None:
    """
    Plots shot trajectories from a DataFrame using Plotly.

    This function takes a DataFrame containing shot trajectory data and uses
    Plotly Express to create a line plot. The plot visualizes the x (distance)
    and y (height) coordinates of each shot, with each shot being represented
    by a different color. The plot is then displayed in a Streamlit app.

    Args:
        df (pd.DataFrame): A DataFrame containing shot data with columns 'x',
                           'y', and 'Shot' for the shot coordinates and labels.

    Returns:
        None: This function does not return any value. It displays the plot in
              a Streamlit application.
    """
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


def plot_club_distribution_stats(
    df: pd.DataFrame,
    dist_metric: str
) -> None:
    """
    Plots the distribution of a specified distance metric for each club.

    This function generates a line plot using Plotly, visualizing the specified
    distance metric (e.g., shot distance, club distance) for each club. The plot
    displays a separate line for each club and marks data points with circles.
    The resulting plot is displayed in a Streamlit app.

    Args:
        df (pd.DataFrame): A DataFrame containing the club data with columns
                           'Club' for the club names and the distance metric
                           as a numeric column.
        dist_metric (str): The column name in the DataFrame representing the
                           distance metric to be plotted (e.g., shot distance).

    Returns:
        None: This function does not return any value. It displays the plot in
              a Streamlit application.
    """
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
