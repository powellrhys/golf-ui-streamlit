# Import dependencies
from frontend.functions.plots import plot_final_trajectory_contour, plot_fairways_hit, plot_strokes_per_hole
import plotly.graph_objects as go
import pandas as pd

def test_plot_final_trajectory_contour_creates_expected_figure():
    # Create dummy input data
    df = pd.DataFrame({
        "x": [0, 1, 2],
        "z": [10, 20, 30]
    })

    # Run the plotting function
    fig = plot_final_trajectory_contour(df)

    # Check that the function returns a Plotly Figure
    assert isinstance(fig, go.Figure)

    # It should contain 2 traces (contour + scatter)
    assert len(fig.data) == 2

    # First trace should be a Histogram2dContour using z and x
    contour = fig.data[0]
    assert isinstance(contour, go.Histogram2dContour)
    assert list(contour.x) == [10, 20, 30]
    assert list(contour.y) == [0, 1, 2]

    # Second trace should be a Scatter with matching x/y
    scatter = fig.data[1]
    assert isinstance(scatter, go.Scatter)
    assert list(scatter.x) == [10, 20, 30]
    assert list(scatter.y) == [0, 1, 2]
    assert scatter.mode == "markers"

def test_plot_fairways_hit_creates_expected_figure():
    # Sample fairway data
    df = pd.DataFrame({
        "Fairway": ["Left", "Target", "Right"],
        "Count": [5, 10, 3]
    })

    # Run the plotting function
    fig = plot_fairways_hit(df)

    # Ensure return type is correct
    assert isinstance(fig, go.Figure)

    # It should have exactly 2 traces (Bar + Pie)
    assert len(fig.data) == 2

    # First trace is a Bar chart
    bar = fig.data[0]
    assert isinstance(bar, go.Bar)
    assert list(bar.x) == ["Left", "Target", "Right"]
    assert list(bar.y) == [5, 10, 3]
    assert list(bar.text) == [5, 10, 3]
    # Colors should match the colour_map defined in the function
    assert list(bar.marker.color) == ["#FF2B2B", "#3B82F6", "#2E7E00"]

    # Second trace is a Pie chart
    pie = fig.data[1]
    assert isinstance(pie, go.Pie)
    assert list(pie.labels) == ["Left", "Target", "Right"]
    assert list(pie.values) == [5, 10, 3]
    assert pie.hole == 0.4
    assert list(pie.marker.colors) == ["#FF2B2B", "#3B82F6", "#2E7E00"]

    # Layout settings should be updated
    assert fig.layout.showlegend is True
    assert fig.layout.bargap == 0.1

def test_plot_strokes_per_hole_creates_expected_figure():
    # Sample strokes data
    df = pd.DataFrame({
        "date_str": ["2025-09-01", "2025-09-01", "2025-09-02"],
        "Strokes": [4, 3, 5],
        "result": ["Par", "Birdie", "Bogey"]
    })

    # Run the plotting function
    fig = plot_strokes_per_hole(df)

    # Check return type
    assert isinstance(fig, go.Figure)

    # There should be one trace per 'result' category present in df
    trace_results = [trace.name for trace in fig.data]
    assert set(trace_results) == set(df["result"])

    # Check the x-values of the first trace match date_str
    assert list(fig.data[0].x) == ["2025-09-01", "2025-09-02"] or list(fig.data[0].x) == ["2025-09-01"]

    # Confirm text is placed inside bars
    for trace in fig.data:
        assert trace.textposition == "inside"

    # Layout checks
    assert fig.layout.xaxis.type == "category"
    assert fig.layout.xaxis.title.text == "Date"
    assert fig.layout.yaxis.title.text == "Strokes"
    assert fig.layout.barmode == "stack"
