# Import python packages
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd

def plot_final_trajectory_contour(df: pd.DataFrame) -> go.Figure:
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

    return fig

def plot_fairways_hit(df: pd.DataFrame) -> go.Figure:
    """
    Plot fairways hit as bar and pie charts.

    Creates a two-panel subplot: a bar chart of fairway outcomes (Left, Target, Right)
    and a pie chart showing the distribution of those outcomes.

    Args: df (pd.DataFrame): DataFrame with columns "Fairway" (str) and "Count" (int).

    Returns: go.Figure: A Plotly figure containing the subplot visualization.
    """
    # Create subplot layout
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "bar"}, {"type": "domain"}]])

    # Define colour map
    colour_map = ["#FF2B2B", "#3B82F6", "#2E7E00"]

    # Add Bar chart trace to subplot
    fig.add_trace(
        go.Bar(x=df["Fairway"],
               y=df["Count"],
               text=df["Count"],
               textposition="inside",
               marker_color=colour_map,
               showlegend=False), row=1, col=1)

    # Add Pie chart trace to subplot
    fig.add_trace(
        go.Pie(labels=df["Fairway"],
               values=df["Count"],
               marker=dict(colors=colour_map),
               hole=0.4), row=1, col=2)

    # Update figure layout
    fig.update_layout(showlegend=True, bargap=0.1)

    return fig

def plot_strokes_per_hole(df: pd.DataFrame):
    """
    Plot a stacked bar chart of strokes per round.

    Uses Plotly to display strokes grouped by result (e.g., Par, Birdie)
    across rounds, with values annotated inside the bars.

    Args:
        df (pd.DataFrame): DataFrame containing at least 'date_str', 'Strokes',
            and 'result' columns.

    Returns: None
    """
    # Define colour map for plot
    color_map = {
        "Eagle": "#ffee00",
        "Birdie": "#2ca02c",
        "Par": "#1f77b4",
        "Bogey": "#ff7f0e",
        "Double Bogey or worse": "#d62728"
    }

    fig = px.bar(
        data_frame=df,
        x="date_str",
        y="Strokes",
        text="Strokes",
        color="result",
        title="Strokes Per Round Overview",
        barmode="stack",
        category_orders={
            "date_str": df["date_str"].unique(),
            "result": list(color_map.keys())
        },
        color_discrete_map=color_map
    )

    # Place values inside the bars
    fig.update_traces(textposition="inside")

    # Explicitly treat x-axis as categorical
    fig.update_xaxes(type="category", title="Date")
    fig.update_layout(
        yaxis_title="Strokes"
    )

    st.plotly_chart(fig)
