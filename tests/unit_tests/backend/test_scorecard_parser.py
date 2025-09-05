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
    """
    Unit tests for the ScorecardParser.parse_fairways method.

    Ensures that the parser correctly handles cells in a scorecard,
    including missing or malformed elements. Uses mocks to simulate
    Selenium WebElements so tests can run without a browser.
    """

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """Automatically create a ScorecardParser instance for all tests."""
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)

    def test_missing_element(self):
        """
        Test that parse_fairways returns 'N/A' for a cell that raises an
        exception when trying to find the inner element.

        This simulates a missing or malformed element in the scorecard.
        """
        # Cell that raises exception when trying to find the inner div
        mock_cell = MagicMock()
        mock_cell.find_element.side_effect = Exception("Not found")

        result = self.parser.parse_fairways([mock_cell])
        assert result == ['N/A']

class TestParseGIR:
    """
    Unit tests for the ScorecardParser.parse_gir method.

    GIR = "Greens in Regulation", a golf stat indicating whether a player
    reached the green in the expected number of strokes. These tests ensure
    that parse_gir correctly interprets mock cells with class attributes
    indicating GIR status.
    """
    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """
        Automatically create a ScorecardParser instance for all tests.
        """
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)

    def make_mock_cell(self, classes: list[str]):
        """
        Helper to create a mocked Selenium WebElement with specific CSS
        class names.

        The mock returns the given class names as a space-separated string
        when its get_attribute("class") method is called.
        """
        mock_cell = MagicMock()
        mock_cell.get_attribute.return_value = " ".join(classes)
        return mock_cell

    def test_all_true_and_false(self):
        """
        Test that parse_gir correctly maps mock cells with various class
        combinations into a list of boolean values.
        """
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
        """
        Test that parse_gir returns an empty list if given no cells.

        Ensures the method gracefully handles the edge case of an empty input.
        """
        result = self.parser.parse_gir([])
        assert result == []


class TestParseStrokes:
    """
    Unit tests for the ScorecardParser.parse_strokes method.

    Strokes represent the number of shots taken on a hole. These tests
    verify that parse_strokes correctly extracts stroke values from
    mocked Selenium WebElements, and handles missing or invalid cases
    gracefully.
    """
    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """Automatically create a ScorecardParser instance for all tests."""
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)

    def make_mock_cell(self, html_value=None, raise_exception=False):
        """
        Helper to create a mocked Selenium WebElement for a stroke cell.

        Args:
            html_value (str | None): The text content of the score-value div.
            raise_exception (bool): If True, calling find_element will
                                    raise an Exception to simulate a missing element.

        Returns:
            MagicMock: A mock object that simulates a Selenium WebElement.
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
        """
        Test that valid numeric strokes are extracted as strings.
        Example: cells with "3", "4", "2" should return ["3", "4", "2"].
        """
        cells = [
            self.make_mock_cell("3"),
            self.make_mock_cell("4"),
            self.make_mock_cell("2")
        ]
        expected = ["3", "4", "2"]
        result = self.parser.parse_strokes(cells)
        assert result == expected

    def test_missing_strokes(self):
        """
        Test that missing strokes return None values.
        """
        cells = [
            self.make_mock_cell(raise_exception=True),
            self.make_mock_cell("&nbsp;"),
            self.make_mock_cell("")
        ]
        expected = [None, None, None]
        result = self.parser.parse_strokes(cells)
        assert result == expected

    def test_mixed_valid_and_missing(self):
        """
        Test that parse_strokes correctly mixes valid strokes with None
        when some cells are invalid.
        Example: ["5", "&nbsp;", "3"] → ["5", None, "3"]
        """
        cells = [
            self.make_mock_cell("5"),
            self.make_mock_cell("&nbsp;"),
            self.make_mock_cell("3")
        ]
        expected = ["5", None, "3"]
        result = self.parser.parse_strokes(cells)
        assert result == expected

    def test_empty_list(self):
        """
        Test that parse_strokes returns an empty list when given no cells.
        """
        result = self.parser.parse_strokes([])
        assert result == []

class TestGetRoundDate:
    """
    Unit tests for the ScorecardParser.get_round_date method.

    This method is expected to locate a <time> element on the page,
    extract its datetime attribute, and return it as a Python date.
    These tests use mocks to simulate Selenium WebDriver behavior
    for valid, invalid, and missing elements.
    """

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """Automatically create a ScorecardParser instance and mock its driver."""
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)
        self.parser.driver = MagicMock()  # mock Selenium WebDriver

    def make_mock_time_element(self, datetime_str):
        """
        Helper to create a mocked <time> element.

        Args:
            datetime_str (str): The value for the element's datetime attribute.

        Returns:
            MagicMock: A mock object simulating a <time> element.
        """
        mock_element = MagicMock()
        mock_element.get_attribute.return_value = datetime_str
        return mock_element

    def test_valid_date(self):
        """
        Test that a valid ISO-8601 datetime string is parsed into a date.
        """
        datetime_str = "2025-09-04T10:30:00Z"
        self.parser.driver.find_element.return_value = self.make_mock_time_element(datetime_str)
        result = self.parser.get_round_date()
        assert result == date(2025, 9, 4)

    def test_invalid_date_format(self):
        """
        Test that an invalid datetime string returns None instead of raising an error.
        """
        datetime_str = "invalid-date"
        self.parser.driver.find_element.return_value = self.make_mock_time_element(datetime_str)
        result = self.parser.get_round_date()
        assert result is None

    def test_missing_element(self):
        """
        Test that if the <time> element cannot be found, the method returns None.

        Simulates Selenium raising an exception when find_element is called.
        """
        self.parser.driver.find_element.side_effect = Exception("Not found")
        result = self.parser.get_round_date()
        assert result is None

class TestGetCourseName:
    """
    Unit tests for the ScorecardParser.get_course_name method.

    This method is expected to locate the course name on the scorecard page,
    extract its text content, and normalize it (e.g., trimming spaces and
    converting spaces to underscores). These tests use mocks to simulate
    Selenium WebDriver behavior.
    """

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """Automatically create a ScorecardParser instance and mock its driver."""
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)
        self.parser.driver = MagicMock()  # mock Selenium WebDriver

    def make_mock_course_element(self, text):
        """
        Helper to create a mocked <p> element with text content.

        Args:
            text (str): The visible text for the element.

        Returns:
            MagicMock: A mock object simulating a Selenium WebElement.
        """
        mock_element = MagicMock()
        mock_element.text = text
        return mock_element

    def test_valid_course_name(self):
        """
        Test that a valid course name is normalized by:
        - trimming whitespace
        - converting to lowercase
        - replacing spaces with underscores.
        """
        self.parser.driver.find_element.return_value = self.make_mock_course_element("Augusta National Golf Club")
        result = self.parser.get_course_name()
        assert result == "augusta_national_golf_club"

    def test_course_name_with_extra_spaces(self):
        """
        Test that leading/trailing spaces are removed before normalization.
        """
        self.parser.driver.find_element.return_value = self.make_mock_course_element("  Pebble Beach  ")
        result = self.parser.get_course_name()
        assert result == "pebble_beach"

    def test_missing_element(self):
        """
        Test that if the course name element cannot be found, the method returns None.

        Simulates Selenium raising an exception when find_element is called.
        """
        self.parser.driver.find_element.side_effect = Exception("Not found")
        result = self.parser.get_course_name()
        assert result is None

    def test_empty_course_name(self):
        """
        Test that if the course name element exists but has no text,
        the method returns an empty string.
        """
        self.parser.driver.find_element.return_value = self.make_mock_course_element("")
        result = self.parser.get_course_name()
        assert result == ""


class TestCleanStrokes:
    """
    Unit tests for the ScorecardParser.clean_strokes method.

    This method is responsible for cleaning raw stroke values
    (extracted from a scorecard) for a given player:
      - Keeps valid numeric stroke values as-is.
      - Converts invalid, empty, or placeholder values into "N/A".
    """

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """
        Automatically create a ScorecardParser instance with a mock player name.
        """
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)

        # Simulate that we're cleaning strokes for "Player1"
        self.parser.vars.round_site_player_name = "Player1"

    def test_numeric_values(self):
        """
        Test that valid numeric strings remain unchanged.
        """
        data = [
            {"Player1": "3"},
            {"Player1": "5"},
            {"Player1": "2"}
        ]
        result = self.parser.clean_strokes(data)
        assert result == data

    def test_mixed_values(self):
        """
        Test that a mix of valid and invalid values is cleaned correctly.
        """
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
    """
    Unit tests for the ScorecardParser.convert_value method.

    This method standardizes raw values (from the scorecard or cleaned data)
    into consistent Python types:
      - Numeric strings → int or float
      - Placeholders ("N/A", "-") → None
      - Booleans and numeric types remain unchanged
      - Other strings are returned as-is
      - None stays None
    """

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """
        Automatically create a ScorecardParser instance before each test.
        """
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)

    def test_various_values(self):
        """
        Test that different types of input values are converted consistently.
        """
        test_cases = {
            5: 5,
            True: True,
            False: False,
            "10": 10,
            "2.71": 2.71,
            "N/A": None,
            "-": None,
            "abc": "abc",
            None: None
        }

        for val, expected in test_cases.items():
            result = self.parser.convert_value(val)
            assert result == expected, f"Failed for value: {val}"


class TestTransformScorecardData:
    """
    Unit tests for the ScorecardParser.transform_scorecard_data method.

    This method converts raw scorecard data (a dict of lists) into a list of
    per-hole dictionaries, always covering 18 holes. If fewer than 18 entries
    are provided, the missing holes are padded with "N/A".
    """
    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """
        Automatically create a ScorecardParser instance before each test.
        """
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)

    def test_basic_transformation(self):
        """
        Test transformation of a short scorecard into a full 18-hole structure.
        """
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
    """
    Unit tests for the ScorecardParser.annotate_results method.

    This method assigns human-readable golf results (e.g., Birdie, Bogey)
    to each hole in the scorecard, based on the difference between strokes
    and par. It also gracefully handles missing values.
    """
    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """
        Automatically create a ScorecardParser instance before each test.
        """
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)

    def test_various_results(self):
        """
        Test that annotate_results correctly labels hole outcomes.
        """
        scorecard = [
            {"hole": 1, "Strokes": 1, "Par": 4},
            {"hole": 2, "Strokes": 2, "Par": 4},
            {"hole": 3, "Strokes": 3, "Par": 4},
            {"hole": 4, "Strokes": 4, "Par": 4},
            {"hole": 5, "Strokes": 5, "Par": 4},
            {"hole": 6, "Strokes": 7, "Par": 4},
            {"hole": 7, "Strokes": None, "Par": 4},
            {"hole": 8, "Strokes": 4, "Par": None}
        ]

        result = self.parser.annotate_results(scorecard)

        expected_results = [
            "Albatross", "Eagle", "Birdie", "Par",
            "Bogey", "Double Bogey or worse",
            None, None
        ]

        for hole, expected in zip(result, expected_results):
            assert hole["result"] == expected
