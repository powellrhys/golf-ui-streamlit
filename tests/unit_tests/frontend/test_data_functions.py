# Import dependencies
from frontend.functions.data_functions import (
    summarise_hole_performance_data,
    collect_yardage_summary_data,
    collect_club_trajectory_data,
    aggregate_fairway_data,
    extract_stat_flags
)
from unittest.mock import patch
import pandas as pd

def test_summarise_hole_performance_data():
    # Mock Variables object
    class MockVariables:
        golf_course_name = "test_course"

    # Mock data
    mock_data = [
        {
            "Hole 1": {
                "Strokes": [4, 5, 4],
                "Par": 4
            }
        },
        {
            "Hole 2": {
                "Strokes": [3, 3, 4],
                "Par": 3
            }
        }
    ]

    # Patch BlobClient.read_blob_to_dict to return mock_data
    with patch("shared.functions.blob_client.BlobClient.read_blob_to_dict", return_value=mock_data):
        df = summarise_hole_performance_data(MockVariables(), rounds=2)

    # Expected dataframe
    expected = pd.DataFrame({
        "Hole": ["Hole 1", "Hole 2"],
        "Avg Strokes": [4.5, 3.0],
        "Par": ["4", "3"],
        "Strokes To Par": ["0.5", "0.0"]
    })

    # Assert dataframes are equal
    pd.testing.assert_frame_equal(df.reset_index(drop=True), expected)

def test_aggregate_fairway_data():
    # Sample input data
    input_data = [
        {"Fairways": "Left"},
        {"Fairways": "Target"},
        {"Fairways": "Right"},
        {"Fairways": "Left"},
        {"Fairways": "Target"},
        {"Fairways": "Left"},
    ]

    # Expected DataFrame after aggregation
    expected_df = pd.DataFrame({
        "Fairway": pd.Categorical(
            ["Left", "Target", "Right"],
            categories=["Left", "Target", "Right"],
            ordered=True
        ),
        "Count": [3, 2, 1]
    })

    # Call the function
    result_df = aggregate_fairway_data(input_data)

    # Use pandas testing function to assert equality
    pd.testing.assert_frame_equal(result_df.reset_index(drop=True), expected_df.reset_index(drop=True))

def test_extract_stat_flags():
    # Case 1: all stats present
    metrics = ["Min Stats", "Max Stats", "Avg Stats"]
    assert extract_stat_flags(metrics) == (True, True, True)

    # Case 2: none present
    metrics = ["Score", "Fairways", "Greens"]
    assert extract_stat_flags(metrics) == (False, False, False)

    # Case 3: some stats present
    metrics = ["Min Stats", "Score", "Avg Stats"]
    assert extract_stat_flags(metrics) == (True, False, True)

    # Case 4: only one stat present
    metrics = ["Max Stats"]
    assert extract_stat_flags(metrics) == (False, True, False)

    # Case 5: empty metrics
    metrics = []
    assert extract_stat_flags(metrics) == (False, False, False)

    # Case 6: metrics as dictionary keys
    metrics = {"Min Stats": 1, "Score": 2}
    assert extract_stat_flags(metrics.keys()) == (True, False, False)

def test_collect_club_trajectory_data():
    # Minimal mock data for 2 shots
    mock_data = [
        {
            "Measurement": {
                "Carry": 250,
                "Total": 270,
                "BallSpeed": 150,
                "BallTrajectory": [
                    {"X": 0, "Y": 0, "Z": 0},
                    {"X": 50, "Y": 20, "Z": 15},
                    {"X": 100, "Y": 10, "Z": 30}
                ]
            }
        },
        {
            "Measurement": {
                "Carry": 230,
                "Total": 250,
                "BallSpeed": 145,
                "BallTrajectory": [
                    {"X": 0, "Y": 0, "Z": 0},
                    {"X": 40, "Y": 25, "Z": 10},
                    {"X": 90, "Y": 5, "Z": 25}
                ]
            }
        }
    ]

    # Call the function
    flight_df, end_df, carry, total_dist, ball_speeds = collect_club_trajectory_data(mock_data, total_shots=2)

    # Check the lengths of lists
    assert carry == [250, 230]
    assert total_dist == [270, 250]
    assert ball_speeds == [150, 145]

    # Check flight_df structure
    assert list(flight_df.columns) == ["x", "y", "Shot"]
    assert set(flight_df["Shot"]) == {"Shot 1", "Shot 2"}
    # Check first shot trajectory values
    first_shot = flight_df[flight_df["Shot"] == "Shot 1"].reset_index(drop=True)
    assert first_shot["x"].tolist() == [0, 50, 100]
    assert first_shot["y"].tolist() == [0, 20, 10]

    # Check end_df structure and values
    assert list(end_df.columns) == ["x", "z", "Shot"]
    assert end_df["x"].tolist() == [100, 90]
    assert end_df["z"].tolist() == [30, 25]

def test_collect_yardage_summary_data():
    # Mock data returned by the BlobClient
    mock_blob_data = [
        {"Driver": {"min_carry": 200, "max_carry": 250, "avg_carry": 225}},
        {"Iron": {"min_carry": 150, "max_carry": 180, "avg_carry": 165}}
    ]

    # Patch the BlobClient to return our mock data
    with patch("shared.functions.blob_client.BlobClient") as MockBlobClient:
        mock_instance = MockBlobClient.return_value
        mock_instance.read_blob_to_dict.return_value = mock_blob_data

        # Call the function
        yardage_df, df_long = collect_yardage_summary_data(
            number_of_shots=10,
            min_stats=True,
            max_stats=True,
            avg_stats=True,
            dist_metric="Carry"
        )

    # Check that yardage_df contains expected columns
    expected_columns = ["Club", "min_carry", "max_carry", "avg_carry"]
    for col in expected_columns:
        assert col in yardage_df.columns

    # Check df_long structure
    assert list(df_long.columns) == ["Club", "carry", "Carry"]
