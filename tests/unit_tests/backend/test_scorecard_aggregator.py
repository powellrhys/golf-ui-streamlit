# Import dependencies
from backend.functions.scorecard_aggregator import RoundAggregator
from unittest.mock import MagicMock
import pytest

@pytest.fixture
def mock_logger():
    """
    Provide a fake logger to satisfy the RoundAggregator constructor.
    We use MagicMock so we can track calls if needed.
    """
    return MagicMock()


@pytest.fixture
def aggregator(mock_logger):
    """
    Create a RoundAggregator instance with mocked dependencies.
    Override the golf_course_name so file paths are consistent.
    """
    agg = RoundAggregator(logger=mock_logger)
    agg.vars.golf_course_name = "new_york"
    return agg


class TestRoundAggregator:
    def test_summarize_course_strokes(self, aggregator):
        """
        Test that summarize_course_strokes:
        - Reads data for all 18 holes
        - Aggregates par and strokes correctly
        - Exports the result with the correct filename
        """
        # Arrange: fake hole data to be returned by read_blob_to_dict
        fake_hole_data = [
            {"Par": 4, "Strokes": 5},
            {"Par": 4, "Strokes": 3}
        ]

        # Patch read_blob_to_dict to always return the same fake hole data
        aggregator.read_blob_to_dict = MagicMock(return_value=fake_hole_data)

        # Patch export_dict_to_blob so nothing is actually written
        aggregator.export_dict_to_blob = MagicMock()

        # Act: run the method
        aggregator.summarize_course_strokes()

        # Assert: ensure read_blob_to_dict was called once per hole (18 total)
        assert aggregator.read_blob_to_dict.call_count == 18

        # Capture the export call arguments
        args, kwargs = aggregator.export_dict_to_blob.call_args
        strokes_summary = kwargs["data"]

        # The exported data should be a list of 18 dictionaries
        assert isinstance(strokes_summary, list)
        assert len(strokes_summary) == 18

        # Verify structure of the first hole’s data
        first_hole = strokes_summary[0]["Hole 1"]
        assert first_hole["Par"] == 4
        assert first_hole["Strokes"] == [5, 3]

        # Verify the exported filename is correct
        assert kwargs["output_filename"] == "new_york_golf_course_hole_summary/course_overview.json"

    def test_aggregate_holes_by_course(self, aggregator):
        """
        Test that aggregate_holes_by_course:
        - Reads only valid JSON files for the correct course
        - Aggregates hole data into a date-sorted list
        - Exports results with the correct filename
        """
        # Arrange: patch list_blob_filenames to return a mix of valid and invalid files
        aggregator.list_blob_filenames = MagicMock(return_value=[
            "scorecards/new_york_2024-01-01.json",     # valid
            "scorecards/new_york_2024-02-01.json",     # valid
            "scorecards/ignore_this.txt",              # should be skipped
            "scorecards/othercourse_2024-01-01.json",  # wrong course, should be skipped
        ])

        # Define fake round data for each valid JSON file
        fake_round_data_1 = [{"hole": 1, "Par": 4, "Strokes": 5}]
        fake_round_data_2 = [{"hole": 1, "Par": 4, "Strokes": 3}]

        # Patch read_blob_to_dict to return different data depending on the call
        aggregator.read_blob_to_dict = MagicMock(side_effect=[fake_round_data_1, fake_round_data_2])

        # Patch export_dict_to_blob so no actual write occurs
        aggregator.export_dict_to_blob = MagicMock()

        # Act: run the method
        aggregator.aggregate_holes_by_course()

        # Assert: only the two valid JSON files should have been read
        assert aggregator.read_blob_to_dict.call_count == 2

        # Only one hole (hole 1) exists in the fake data, so export should be called once
        aggregator.export_dict_to_blob.assert_called_once()

        # Capture export arguments
        args, kwargs = aggregator.export_dict_to_blob.call_args
        exported_data = kwargs["data"]

        # The exported data should be a list of hole entries
        assert isinstance(exported_data, list)

        # Ensure strokes are present and come from both fake round datasets
        strokes = [entry["Strokes"] for entry in exported_data]
        assert 5 in strokes and 3 in strokes

        # Verify the exported filename is correct
        assert kwargs["output_filename"] == "new_york_golf_course_hole_summary/hole_1.json"
