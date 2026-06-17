# Import dependencies
from backend.functions.scorecard_parser import ScorecardParser
from unittest.mock import MagicMock
import logging
import pytest

class TestParseScorecardRowsIntegration:
    """
    Integration tests for parsing scorecard rows.

    Validates that ScorecardParser correctly parses individual
    rows of a scorecard for player strokes and other stats.
    """

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """
        Setup fixture to initialize ScorecardParser.

        Creates a logger and sets the player name for the parser
        to ensure tests are consistent.
        """
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)
        self.parser.vars.round_site_player_name = "Player1"

    def make_mock_cell(self, inner_html=""):
        """
        Create a mock HTML cell element.

        Used to simulate a scorecard cell for strokes or other values.

        Args:
            inner_html (str, optional): HTML content of the cell. Defaults to "".

        Returns:
            MagicMock: Mocked cell element.
        """
        # Mock the div containing the score
        mock_score_div = MagicMock()
        mock_score_div.get_attribute.return_value = inner_html

        # Mock the cell element that contains the div
        mock_cell = MagicMock()
        mock_cell.find_element.return_value = mock_score_div
        return mock_cell

    def make_mock_line(self, label, values):
        """
        Mock a row element with label and multiple cells.

        Args:
            label (str): Label for the row (e.g., player name or Par).
            values (list): List of string values for each cell.

        Returns:
            MagicMock: Mocked row element.
        """
        mock_line = MagicMock()

        # Left side label element
        mock_label_element = MagicMock()
        mock_label_element.text = label
        mock_line.find_element.return_value = mock_label_element

        # Values as mocked cells
        mock_value_elements = [self.make_mock_cell(inner_html=v) for v in values]
        mock_line.find_elements.return_value = mock_value_elements

        return mock_line

class TestCollectScorecardDataIntegration:
    """
    Integration tests for collecting and processing scorecard data.

    Validates that ScorecardParser.collect_scorecard_data correctly
    extracts, transforms, and annotates scorecard data from a URL.
    """

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """
        Fixture to create a ScorecardParser instance with mocked driver.

        Sets the driver to a MagicMock to avoid real web requests
        and sets a fixed player name for testing.
        """
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)
        self.parser.driver = MagicMock()
        self.parser.vars.round_site_player_name = "Player1"

    def make_mock_cell(self, inner_html=""):
        """
        Mock a score cell element for strokes or generic values.

        Args:
            inner_html (str, optional): Content of the cell. Defaults to "".

        Returns:
            MagicMock: Mocked cell element.
        """
        mock_score_div = MagicMock()
        mock_score_div.get_attribute.return_value = inner_html
        mock_cell = MagicMock()
        mock_cell.find_element.return_value = mock_score_div
        return mock_cell

    def make_mock_line(self, label, values):
        """
        Mock a row element for parse_scorecard_rows.

        Args:
            label (str): Row label (player name, Par, etc.)
            values (list): List of values for each hole

        Returns:
            MagicMock: Mocked row element.
        """
        mock_line = MagicMock()

        # Left side label element
        mock_label_element = MagicMock()
        mock_label_element.text = label
        mock_line.find_element.return_value = mock_label_element

        # Values as mocked cells
        mock_value_elements = [self.make_mock_cell(inner_html=v) for v in values]

        # Use lambda to return the mock cells when find_elements is called
        mock_line.find_elements = lambda *args, **kwargs: mock_value_elements
        return mock_line

    def test_collect_scorecard_data_basic(self):
        """
        Integration test for collect_scorecard_data.

        Mocks round date, course name, and scorecard rows to validate
        that the parser collects, transforms, and annotates data
        correctly into a structured format.
        """
        # Mock get_round_date element
        mock_date_element = MagicMock()
        mock_date_element.text = "21/06/2025"

        # Mock get_course_name element
        mock_course_element = MagicMock()
        mock_course_element.text = "Augusta National"

        # Mock scorecard section with multiple rows
        mock_section = MagicMock()
        mock_section.find_elements = lambda *args, **kwargs: [
            self.make_mock_line("Player1", ["3", "4", "5"]),
            self.make_mock_line("Par", ["4", "5", "3"])
        ]

        # Side effect for driver.find_element to return mocks in order
        self.parser.driver.find_element.side_effect = [
            mock_date_element,
            mock_course_element,
            mock_section
        ]

        # Run the integration method
        url = "http://fake-url.com/scorecard"
        scorecard, file_name = self.parser.collect_scorecard_data(url)

        # Assertions on returned data
        assert isinstance(scorecard, list)
        assert "Par" in scorecard[0]
        assert "hole" in scorecard[0]
        assert "result" in scorecard[0]
        assert file_name.startswith("scorecards/augusta_national_2025-06-21")
