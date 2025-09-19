# Import dependencies
from unittest.mock import patch, MagicMock
from frontend import display_club_summary_shot_trajectories, display_club_metrics

def test_display_club_metrics():
    # Test data
    total_shots = 5
    carry_data = [200, 210, 190, 205, 195]
    total_distance = [220, 230, 210, 225, 215]
    ball_speeds = [145, 150, 148, 147, 149]

    # Expected averages
    expected_carry = f"{round(sum(carry_data) / len(carry_data), 2)}m"
    expected_distance = f"{round(sum(total_distance) / len(total_distance), 2)}m"
    expected_speed = f"{round(sum(ball_speeds) / len(ball_speeds), 2)}mph"

    with patch("frontend.functions.ui_components.st") as mock_st:  # Patch the Streamlit module
        # Mock the columns
        mock_col = MagicMock()
        mock_st.columns.return_value = (mock_col, mock_col, mock_col)

        # Call the function
        display_club_metrics(total_shots, carry_data, total_distance, ball_speeds)

        # Assertions
        mock_st.columns.assert_called_with(3)

        # Extract calls to st.metric
        metric_calls = mock_st.metric.call_args_list

        # Check that each metric was called with the expected values
        assert any(call.kwargs["value"] == expected_carry for call in metric_calls)
        assert any(call.kwargs["value"] == expected_distance for call in metric_calls)
        assert any(call.kwargs["value"] == expected_speed for call in metric_calls)

def test_display_club_summary_shot_trajectories():
    # Create fake shot data input (just needs to be non-empty)
    fake_data = [{"x": 1, "y": 2, "carry": 200, "total": 250, "speed": 140}]

    # Create fake outputs for collect_club_trajectory_data so we don't rely on real calculations
    fake_final_flight_df = MagicMock()
    fake_final_end_df = MagicMock()
    fake_carry = [200, 210]
    fake_total = [250, 260]
    fake_speeds = [140, 142]

    # Patch all external dependencies this function calls
    with patch("frontend.functions.ui_components.collect_club_trajectory_data") as mock_collect, \
         patch("frontend.functions.ui_components.display_club_metrics") as mock_metrics, \
         patch("frontend.functions.ui_components.st.expander") as mock_expander, \
         patch("frontend.functions.ui_components.st.plotly_chart") as mock_plotly_chart, \
         patch("frontend.functions.ui_components.PlotlyPlotter") as mock_plotter, \
         patch("frontend.functions.ui_components.plot_final_trajectory_contour") as mock_contour:

        # --- Mock setup ---
        # When collect_club_trajectory_data is called, return our fake outputs
        mock_collect.return_value = (
            fake_final_flight_df, fake_final_end_df, fake_carry, fake_total, fake_speeds
        )

        # Make st.expander usable in a `with` block (context manager)
        mock_expander.return_value.__enter__.return_value = MagicMock()
        mock_expander.return_value.__exit__.return_value = False

        # Make PlotlyPlotter().plot_line() return a fake plot object
        mock_plotter.return_value.plot_line.return_value = "fake_plot"

        # --- Act ---
        # Call the function under test
        display_club_summary_shot_trajectories(fake_data, total_shots=2)

        # --- Assert ---
        # Verify collect_club_trajectory_data was called with the right arguments
        mock_collect.assert_called_once_with(data=fake_data, total_shots=2)

        # Verify display_club_metrics was called with the values returned from collect_club_trajectory_data
        mock_metrics.assert_called_once_with(
            total_shots=2,
            carry_data=fake_carry,
            total_distance=fake_total,
            ball_speeds=fake_speeds
        )

        # Verify two expanders were created: "Shot Trajectory" and "Shot Distribution"
        mock_expander.assert_any_call(label="Shot Trajectory", expanded=True)
        mock_expander.assert_any_call(label="Shot Distribution", expanded=True)

        # Verify PlotlyPlotter was called with the correct arguments for the trajectory plot
        mock_plotter.assert_called_once_with(
            df=fake_final_flight_df,
            x='x',
            y='y',
            color='Shot',
            labels={'x': 'Horizontal Distance (m)', 'y': 'Vertical Distance (m)'}
        )

        # Verify st.plotly_chart rendered the fake plot
        mock_plotly_chart.assert_called_once_with("fake_plot")

        # Verify the contour plot function was called with the final end dataframe
        mock_contour.assert_called_once_with(df=fake_final_end_df)
