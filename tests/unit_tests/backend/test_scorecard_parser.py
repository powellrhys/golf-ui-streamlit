# Import dependencies
from backend import ScorecardParser
from unittest.mock import MagicMock
from datetime import date
import logging
import pytest

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

class TestParseFairways:

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """Fixture to create a ScorecardParser instance for all tests."""
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)

    def make_mock_cell(self, classes: list[str]):
        """Create a mocked Selenium WebElement with given class names."""
        mock_hit = MagicMock()
        mock_hit.get_attribute.return_value = " ".join(classes)

        mock_cell = MagicMock()
        mock_cell.find_element.return_value = mock_hit
        return mock_cell

    def test_missing_element(self):
        # Cell that raises exception when trying to find the inner div
        mock_cell = MagicMock()
        mock_cell.find_element.side_effect = Exception("Not found")

        result = self.parser.parse_fairways([mock_cell])
        assert result == ['N/A']

class TestParseGIR:

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """Fixture to create a ScorecardParser instance for all tests."""
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)

    def make_mock_cell(self, classes: list[str]):
        """Create a mocked Selenium WebElement with given class names."""
        mock_cell = MagicMock()
        mock_cell.get_attribute.return_value = " ".join(classes)
        return mock_cell

    def test_all_true_and_false(self):
        # Prepare mock cells
        cells = [
            self.make_mock_cell(['gir', 'true']),
            self.make_mock_cell(['gir', 'false']),
            self.make_mock_cell(['notgir', 'true']),
            self.make_mock_cell([]),
        ]

        expected = [True, False, False, False]
        result = self.parser.parse_gir(cells)
        assert result == expected

    def test_empty_list(self):
        result = self.parser.parse_gir([])
        assert result == []

class TestParseStrokes:

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """Fixture to create a ScorecardParser instance for all tests."""
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)

    def make_mock_cell(self, html_value=None, raise_exception=False):
        """
        Create a mocked Selenium WebElement for a stroke cell.
        :param html_value: HTML content of the score-value div
        :param raise_exception: if True, cell.find_element raises an Exception
        """
        mock_cell = MagicMock()
        if raise_exception:
            mock_cell.find_element.side_effect = Exception("Not found")
        else:
            mock_score_div = MagicMock()
            mock_score_div.get_attribute.return_value = html_value or ""
            mock_cell.find_element.return_value = mock_score_div
        return mock_cell

    def test_valid_strokes(self):
        cells = [
            self.make_mock_cell("3"),
            self.make_mock_cell("4"),
            self.make_mock_cell("2")
        ]
        expected = ["3", "4", "2"]  # parse_strokes currently returns strings, not ints
        result = self.parser.parse_strokes(cells)
        assert result == expected

    def test_missing_strokes(self):
        cells = [
            self.make_mock_cell(raise_exception=True),
            self.make_mock_cell("&nbsp;"),
            self.make_mock_cell("")
        ]
        expected = [None, None, None]
        result = self.parser.parse_strokes(cells)
        assert result == expected

    def test_mixed_valid_and_missing(self):
        cells = [
            self.make_mock_cell("5"),
            self.make_mock_cell("&nbsp;"),
            self.make_mock_cell("3")
        ]
        expected = ["5", None, "3"]
        result = self.parser.parse_strokes(cells)
        assert result == expected

    def test_empty_list(self):
        result = self.parser.parse_strokes([])
        assert result == []

class TestGetRoundDate:

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """Fixture to create a ScorecardParser instance for all tests."""
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)
        self.parser.driver = MagicMock()  # mock Selenium driver

    def make_mock_time_element(self, datetime_str):
        """Create a mocked <time> element with a datetime attribute."""
        mock_element = MagicMock()
        mock_element.get_attribute.return_value = datetime_str
        return mock_element

    def test_valid_date(self):
        datetime_str = "2025-09-04T10:30:00Z"
        self.parser.driver.find_element.return_value = self.make_mock_time_element(datetime_str)
        result = self.parser.get_round_date()
        assert result == date(2025, 9, 4)

    def test_invalid_date_format(self):
        datetime_str = "invalid-date"
        self.parser.driver.find_element.return_value = self.make_mock_time_element(datetime_str)
        result = self.parser.get_round_date()
        assert result is None

    def test_missing_element(self):
        self.parser.driver.find_element.side_effect = Exception("Not found")
        result = self.parser.get_round_date()
        assert result is None

class TestGetCourseName:

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """Fixture to create a ScorecardParser instance for all tests."""
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)
        self.parser.driver = MagicMock()  # mock Selenium driver

    def make_mock_course_element(self, text):
        """Create a mocked <p> element with a text attribute."""
        mock_element = MagicMock()
        mock_element.text = text
        return mock_element

    def test_valid_course_name(self):
        self.parser.driver.find_element.return_value = self.make_mock_course_element("Augusta National Golf Club")
        result = self.parser.get_course_name()
        assert result == "augusta_national_golf_club"  # lowercased and underscores

    def test_course_name_with_extra_spaces(self):
        self.parser.driver.find_element.return_value = self.make_mock_course_element("  Pebble Beach  ")
        result = self.parser.get_course_name()
        assert result == "pebble_beach"

    def test_missing_element(self):
        self.parser.driver.find_element.side_effect = Exception("Not found")
        result = self.parser.get_course_name()
        assert result is None

    def test_empty_course_name(self):
        self.parser.driver.find_element.return_value = self.make_mock_course_element("")
        result = self.parser.get_course_name()
        assert result == ""

class TestCleanStrokes:

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """Fixture to create a ScorecardParser instance."""
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)
        # set a mock player name
        self.parser.vars.round_site_player_name = "Player1"

    def test_numeric_values(self):
        data = [
            {"Player1": "3"},
            {"Player1": "5"},
            {"Player1": "2"}
        ]
        result = self.parser.clean_strokes(data)
        assert result == data  # numeric strings remain unchanged

    def test_invalid_values(self):
        data = [
            {"Player1": "abc"},
            {"Player1": ""},
            {"Player1": None},
            {"Player1": "&nbsp;"}
        ]
        result = self.parser.clean_strokes(data)
        expected = [
            {"Player1": "N/A"},
            {"Player1": "N/A"},
            {"Player1": "N/A"},
            {"Player1": "N/A"}
        ]
        assert result == expected

    def test_mixed_values(self):
        data = [
            {"Player1": "3"},
            {"Player1": "abc"},
            {"Player1": None}
        ]
        result = self.parser.clean_strokes(data)
        expected = [
            {"Player1": "3"},
            {"Player1": "N/A"},
            {"Player1": "N/A"}
        ]
        assert result == expected


class TestConvertValue:

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """Fixture to create a ScorecardParser instance."""
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)

    def test_various_values(self):
        test_cases = {
            5: 5,                          # int stays int
            True: True,                      # bool unchanged
            False: False,                    # bool unchanged
            "10": 10,                        # numeric string converted to int
            "2.71": 2.71,                    # numeric string converted to float
            "N/A": None,                     # placeholder -> None
            "-": None,                        # placeholder -> None
            "abc": "abc",                     # other string unchanged
            None: None                        # None unchanged
        }

        for val, expected in test_cases.items():
            result = self.parser.convert_value(val)
            assert result == expected, f"Failed for value: {val}"

class TestTransformScorecardData:

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """Fixture to create a ScorecardParser instance."""
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)

    def test_basic_transformation(self):
        scorecard_data = {
            "Par": ["4", "5", "3"],
            "Player1": ["3", "4", "5"]
        }
        result = self.parser.transform_scorecard_data(scorecard_data)

        # Check total holes
        assert len(result) == 18

        # Check first hole
        assert result[0]["hole"] == 1
        assert result[0]["Par"] == "4"
        assert result[0]["Player1"] == "3"

        # Check third hole
        assert result[2]["hole"] == 3
        assert result[2]["Par"] == "3"
        assert result[2]["Player1"] == "5"

        # Check holes beyond input get "N/A"
        for i in range(3, 18):
            assert result[i]["Par"] == "N/A"
            assert result[i]["Player1"] == "N/A"

class TestAnnotateResults:

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """Fixture to create a ScorecardParser instance."""
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)

    def test_various_results(self):
        scorecard = [
            {"hole": 1, "Strokes": 1, "Par": 4},   # Albatross
            {"hole": 2, "Strokes": 2, "Par": 4},   # Eagle
            {"hole": 3, "Strokes": 3, "Par": 4},   # Birdie
            {"hole": 4, "Strokes": 4, "Par": 4},   # Par
            {"hole": 5, "Strokes": 5, "Par": 4},   # Bogey
            {"hole": 6, "Strokes": 7, "Par": 4},   # Double Bogey or worse
            {"hole": 7, "Strokes": None, "Par": 4},  # Missing strokes
            {"hole": 8, "Strokes": 4, "Par": None}  # Missing par
        ]

        result = self.parser.annotate_results(scorecard)

        expected_results = [
            "Albatross", "Eagle", "Birdie", "Par", "Bogey", "Double Bogey or worse", None, None
        ]

        for hole, expected in zip(result, expected_results):
            assert hole["result"] == expected
