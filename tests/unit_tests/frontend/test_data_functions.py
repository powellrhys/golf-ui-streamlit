# Import functions to be tested and dependencies
from frontend.functions.data_functions import (
    summarise_hole_performance_data,
    collect_club_trajectory_data,
    aggregate_fairway_data,
    extract_stat_flags
)
from unittest.mock import patch
import pandas as pd

def test_summarise_hole_performance_data():
    # Define a mock variables class with a test course name
    class MockVariables:
        golf_course_name = "test_course"

    # Create mock hole data that simulates blob storage input
    mock_data = [
        {"Hole 1": {"Strokes": [4, 5, 4], "Par": 4}},
        {"Hole 2": {"Strokes": [3, 3, 4], "Par": 3}}
    ]

    # Patch blob reading and secrets configuration to return mock data
    with patch("shared.functions.blob_client.BlobClient.read_blob_to_dict", return_value=mock_data), \
         patch("shared.functions.variables.st.secrets",
               {"general": {
                   "blob_storage_connection_string": "fake",
                   "golf_course_name": "test_course"
               }}):
        # Call the function under test
        df = summarise_hole_performance_data(MockVariables(), rounds=2)

    # Assert that the returned DataFrame is valid and has expected columns
    assert not df.empty
    assert "Hole" in df.columns
    assert "Avg Strokes" in df.columns

def test_aggregate_fairway_data():
    # Sample input representing fairway shot directions
    input_data = [
        {"Fairways": "Left"},
        {"Fairways": "Target"},
        {"Fairways": "Right"},
        {"Fairways": "Left"},
        {"Fairways": "Target"},
        {"Fairways": "Left"},
    ]

    # Define expected DataFrame output after aggregation
    expected_df = pd.DataFrame({
        "Fairway": pd.Categorical(
            ["Left", "Target", "Right"],
            categories=["Left", "Target", "Right"],
            ordered=True
        ),
        "Count": [3, 2, 1]
    })

    # Call the function to aggregate fairway data
    result_df = aggregate_fairway_data(input_data)

    # Compare the actual DataFrame with the expected one
    pd.testing.assert_frame_equal(result_df.reset_index(drop=True), expected_df.reset_index(drop=True))

def test_extract_stat_flags():
    # Test when all relevant stats are present
    metrics = ["Min Stats", "Max Stats", "Avg Stats"]
    assert extract_stat_flags(metrics) == (True, True, True)

    # Test when no relevant stats are present
    metrics = ["Score", "Fairways", "Greens"]
    assert extract_stat_flags(metrics) == (False, False, False)

    # Test when some relevant stats are present
    metrics = ["Min Stats", "Score", "Avg Stats"]
    assert extract_stat_flags(metrics) == (True, False, True)

    # Test when only one stat is present
    metrics = ["Max Stats"]
    assert extract_stat_flags(metrics) == (False, True, False)

    # Test with an empty metrics list
    metrics = []
    assert extract_stat_flags(metrics) == (False, False, False)

    # Test with metrics as dictionary keys
    metrics = {"Min Stats": 1, "Score": 2}
    assert extract_stat_flags(metrics.keys()) == (True, False, False)

def test_collect_club_trajectory_data():
    # Minimal mock data simulating two shots with measurement details
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

    # Call the function to process club trajectory data
    flight_df, end_df, carry, total_dist, ball_speeds = collect_club_trajectory_data(mock_data, total_shots=2)

    # Assert that carry, total distance, and ball speeds are correct
    assert carry == [250, 230]
    assert total_dist == [270, 250]
    assert ball_speeds == [150, 145]

    # Check that flight_df contains expected columns and shot labels
    assert list(flight_df.columns) == ["x", "y", "Shot"]
    assert set(flight_df["Shot"]) == {"Shot 1", "Shot 2"}

    # Verify trajectory values for the first shot
    first_shot = flight_df[flight_df["Shot"] == "Shot 1"].reset_index(drop=True)
    assert first_shot["x"].tolist() == [0, 50, 100]
    assert first_shot["y"].tolist() == [0, 20, 10]

    # Check that end_df contains expected columns and values
    assert list(end_df.columns) == ["x", "z", "Shot"]
    assert end_df["x"].tolist() == [100, 90]
    assert end_df["z"].tolist() == [30, 25]
