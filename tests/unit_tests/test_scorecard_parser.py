# Import dependencies
from backend import ScorecardParser
import logging

class TestDropUnplayedHoles:
    """
    Unit tests for ScorecardParser.drop_unplayed_holes.

    Ensures holes with missing stroke values are correctly filtered out.
    """
    def setup_method(self):
        """
        Set up a ScorecardParser instance for testing.
        """
        self.obj = ScorecardParser(logger=logging.getLogger('BASIC'))

    def test_removes_entries_with_none_strokes(self):
        """
        Holes with `Strokes = None` should be excluded from the result.
        """
        # Define input data
        data = [
            {"Hole": 1, "Strokes": 4},
            {"Hole": 2, "Strokes": None},
            {"Hole": 3, "Strokes": 5},
        ]

        # Collect function output
        result = self.obj.drop_unplayed_holes(data)

        # Validate Result
        assert result == [
            {"Hole": 1, "Strokes": 4},
            {"Hole": 3, "Strokes": 5},
        ]

    def test_returns_empty_when_all_none(self):
        """
        If all holes have `Strokes = None`, the result should be empty.
        """
        # Define input data
        data = [
            {"Hole": 1, "Strokes": None},
            {"Hole": 2, "Strokes": None},
        ]

        # Collect function output
        result = self.obj.drop_unplayed_holes(data)

        # Validate Result
        assert result == []

    def test_returns_all_when_no_none(self):
        """
        If no holes have `Strokes = None`, the result should remain unchanged.
        """
        # Define input data
        data = [
            {"Hole": 1, "Strokes": 3},
            {"Hole": 2, "Strokes": 4},
        ]

        # Collect function output
        result = self.obj.drop_unplayed_holes(data)

        # Validate Result
        assert result == data


class TestConvertPlayerToStrokeKey:
    """
    Unit tests for ScorecardParser.convert_player_to_stroke_key.

    Ensures player-specific stroke values are mapped to a unified "Strokes" key.
    """
    def setup_method(self):
        """
        Set up a ScorecardParser instance with a mock player name.
        """
        self.obj = ScorecardParser(logger=logging.getLogger('BASIC'))

        # Define dummy Vars Class
        class Vars:
            round_site_player_name = "Alice"
        self.obj.vars = Vars()

    def test_converts_player_scores_to_strokes(self):
        """
        Player scores should be moved into the "Strokes" key for each hole.
        """
        # Define input data
        data = [
            {"Hole": 1, "Alice": 4, "Bob": 5},
            {"Hole": 2, "Alice": 3, "Bob": 4},
        ]

        # Collect function output
        result = self.obj.convert_player_to_stroke_key(data)

        # Define expected result
        expected = [
            {"Hole": 1, "Strokes": 4, "Bob": 5},
            {"Hole": 2, "Strokes": 3, "Bob": 4},
        ]

        # Validate Result
        assert result == expected

    def test_returns_empty_list_when_no_holes(self):
        """
        An empty scorecard list should return an empty list.
        """
        # Define input data
        data = []

        # Collect function output
        result = self.obj.convert_player_to_stroke_key(data)

        # Validate Result
        assert result == []

    def test_ignores_holes_without_player_name(self):
        """
        Holes missing the player's name should remain unchanged.
        """
        # Define input data
        data = [
            {"Hole": 1, "Bob": 5},
            {"Hole": 2, "Bob": 4},
        ]

        # Collect function output
        result = self.obj.convert_player_to_stroke_key(data)

        # Validate Result
        assert result == data
