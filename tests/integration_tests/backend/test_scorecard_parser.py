import pytest
from unittest.mock import MagicMock
from backend import ScorecardParser
import logging

class TestParseScorecardRowsIntegration:

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)
        self.parser.vars.round_site_player_name = "Player1"

    def make_mock_cell(self, inner_html=""):
        mock_score_div = MagicMock()
        mock_score_div.get_attribute.return_value = inner_html  # value that parse_strokes expects
        mock_cell = MagicMock()
        mock_cell.find_element.return_value = mock_score_div
        return mock_cell

    def make_mock_line(self, label, values):
        """Mock a row element with label and multiple cells."""
        mock_line = MagicMock()

        # Left side label element
        mock_label_element = MagicMock()
        mock_label_element.text = label
        mock_line.find_element.return_value = mock_label_element

        # Values
        mock_value_elements = [self.make_mock_cell(inner_html=v) for v in values]

        mock_line.find_elements.return_value = mock_value_elements

        return mock_line

    def test_parse_player_strokes_row(self):
        """Test parsing a player strokes row."""
        line = self.make_mock_line("Player1", ["3", "4", "5"])
        scorecard_data = {}
        result = self.parser.parse_scorecard_rows(line, scorecard_data)

        # Verify keys
        assert "Player1" in result
        assert result["Player1"] == ["3", "4", "5"]

class TestCollectScorecardDataIntegration:

    @pytest.fixture(autouse=True)
    def setup_parser(self):
        """Fixture to create a ScorecardParser instance with mocked driver."""
        logger = logging.getLogger("test_logger")
        self.parser = ScorecardParser(logger=logger)
        self.parser.driver = MagicMock()  # Mock Selenium driver
        self.parser.vars.round_site_player_name = "Player1"

    def make_mock_cell(self, inner_html=""):
        """Mock a score cell element for strokes or generic values."""
        mock_score_div = MagicMock()
        mock_score_div.get_attribute.return_value = inner_html
        mock_cell = MagicMock()
        mock_cell.find_element.return_value = mock_score_div
        return mock_cell

    def make_mock_line(self, label, values):
        """Mock a row element for parse_scorecard_rows."""
        mock_line = MagicMock()

        # Left side label element
        mock_label_element = MagicMock()
        mock_label_element.text = label
        mock_line.find_element.return_value = mock_label_element

        # Values
        mock_value_elements = [self.make_mock_cell(inner_html=v) for v in values]
        mock_line.find_elements = lambda *args, **kwargs: mock_value_elements
        return mock_line

    def test_collect_scorecard_data_basic(self):
        """Integration test for collect_scorecard_data."""

        # Mock get_round_date
        mock_time_element = MagicMock()
        mock_time_element.get_attribute.return_value = "2025-09-04T10:30:00Z"

        # Mock get_course_name
        mock_course_element = MagicMock()
        mock_course_element.text = "Augusta National"

        # Mock scorecard section
        mock_section = MagicMock()
        mock_section.find_elements = lambda *args, **kwargs: [
            self.make_mock_line("Player1", ["3", "4", "5"]),
            self.make_mock_line("Par", ["4", "5", "3"])
        ]

        # Define side_effect for driver.find_element to return mocks in order
        self.parser.driver.find_element.side_effect = [
            mock_time_element,    # get_round_date
            mock_course_element,  # get_course_name
            mock_section          # scorecard_section
        ]

        # Run the integration method
        url = "http://fake-url.com/scorecard"
        scorecard, file_name = self.parser.collect_scorecard_data(url)

        # Assertions
        assert isinstance(scorecard, list)
        assert "Strokes" in scorecard[0]
        assert "Par" in scorecard[0]
        assert "hole" in scorecard[0]
        assert "result" in scorecard[0]
        assert file_name.startswith("scorecards/augusta_national_2025-09-04")
