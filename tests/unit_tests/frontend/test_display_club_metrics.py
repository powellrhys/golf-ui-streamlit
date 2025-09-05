# Import dependencies
from unittest.mock import patch, MagicMock
from frontend import display_club_metrics

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
        assert any(
            call.kwargs["value"] == expected_carry for call in metric_calls
        )
        assert any(
            call.kwargs["value"] == expected_distance for call in metric_calls
        )
        assert any(
            call.kwargs["value"] == expected_speed for call in metric_calls
        )
