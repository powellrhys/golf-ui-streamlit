# Import dependencies
from backend import ScorecardParser
import logging

class TestDropUnplayedHoles:
    def setup_method(self):
        self.obj = ScorecardParser(logger=logging.getLogger('BASIC'))

    def test_removes_entries_with_none_strokes(self):
        data = [
            {"Hole": 1, "Strokes": 4},
            {"Hole": 2, "Strokes": None},
            {"Hole": 3, "Strokes": 5},
        ]

        result = self.obj.drop_unplayed_holes(data)

        assert result == [
            {"Hole": 1, "Strokes": 4},
            {"Hole": 3, "Strokes": 5},
        ]

    def test_returns_empty_when_all_none(self):
        data = [
            {"Hole": 1, "Strokes": None},
            {"Hole": 2, "Strokes": None},
        ]

        result = self.obj.drop_unplayed_holes(data)

        assert result == []

    def test_returns_all_when_no_none(self):
        data = [
            {"Hole": 1, "Strokes": 3},
            {"Hole": 2, "Strokes": 4},
        ]

        result = self.obj.drop_unplayed_holes(data)

        assert result == data


class TestConvertPlayerToStrokeKey:
    def setup_method(self):
        self.obj = ScorecardParser(logger=logging.getLogger('BASIC'))

        class Vars:
            round_site_player_name = "Alice"
        self.obj.vars = Vars()

    def test_converts_player_scores_to_strokes(self):
        data = [
            {"Hole": 1, "Alice": 4, "Bob": 5},
            {"Hole": 2, "Alice": 3, "Bob": 4},
        ]

        result = self.obj.convert_player_to_stroke_key(data)

        expected = [
            {"Hole": 1, "Strokes": 4, "Bob": 5},
            {"Hole": 2, "Strokes": 3, "Bob": 4},
        ]

        assert result == expected

    def test_returns_empty_list_when_no_holes(self):
        data = []

        result = self.obj.convert_player_to_stroke_key(data)

        assert result == []

    def test_ignores_holes_without_player_name(self):
        data = [
            {"Hole": 1, "Bob": 5},
            {"Hole": 2, "Bob": 4},
        ]

        result = self.obj.convert_player_to_stroke_key(data)

        # Should remain unchanged because "Alice" is not in any hole
        assert result == data
