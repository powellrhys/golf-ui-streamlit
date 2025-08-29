# Import dependencies
from selenium.webdriver.common.by import By
from .selenium_driver import SeleniumDriver
from datetime import datetime, date
from shared import Variables
import logging
import re

class ScorecardParser(SeleniumDriver):
    """
    Parses golf scorecards from the Hole19 website.

    Uses Selenium to extract round details, clean raw HTML data, and
    transform it into structured hole-level records.
    """
    def __init__(self, logger: logging.Logger,
                 driver_path: str = 'chromedriver.exe',
                 headless: bool = False) -> None:
        """
        Initialize the ScorecardParser.

        Sets up logging, ChromeDriver configuration, and shared variables.

        Args:
            logger (logging.Logger): Logger instance for recording progress and errors.
            driver_path (str, optional): Path to the ChromeDriver executable. Defaults to 'chromedriver.exe'.
            headless (bool, optional): Whether to run Chrome in headless mode. Defaults to False.
        """
        super().__init__()
        self.driver_path = driver_path
        self.headless = headless
        self.logger = logger
        self.vars = Variables()

    def initiate_driver(self) -> None:
        """
        Configure and start the Selenium WebDriver.

        Creates a ChromeDriver instance with the given path and headless setting.

        Returns: None
        """
        self.driver = self.configure_driver(driver_path=self.driver_path, headless=self.headless)

    def parse_fairways(self, cell_elements: list) -> list[str]:
        """
        Parse fairway hit directions.

        Extracts whether each tee shot went left, right, target, or was unavailable.

        Args: cell_elements (list): List of HTML cell elements representing fairway data.

        Returns: list[str]: List of fairway directions per hole.
        """
        # Define empty direction list
        directions = []

        # Iterate through cell elements
        for cell in cell_elements:

            # Map fairway direction object to corresponding text
            try:
                hit = cell.find_element(By.CSS_SELECTOR, 'div.fairway-hit.scorecard-icon')
                classes = hit.get_attribute('class').split()
                if 'left' in classes:
                    directions.append('Left')
                elif 'target' in classes:
                    directions.append('Target')
                elif 'right' in classes:
                    directions.append('Right')
                else:
                    directions.append('N/A')
            except BaseException:
                directions.append('N/A')

            return directions

    def parse_gir(self, cell_elements: list) -> list[bool]:
        """
        Parse greens in regulation (GIR).

        Determines whether the green was reached in regulation for each hole.

        Args: cell_elements (list): List of HTML cell elements representing GIR data.

        Returns: list[bool]: True if GIR, False otherwise per hole.
        """
        # Define empty green in regulation list
        gir_results = []

        # Iterate through cell elements and declare if green was hit in regulation
        for cell in cell_elements:
            classes = cell.get_attribute('class').split()
            gir_results.append('gir' in classes and 'true' in classes)

        return gir_results

    def parse_strokes(self, cell_elements: list) -> list[int | None]:
        """
        Parse stroke counts.

        Extracts the number of strokes taken per hole from scorecard cells.

        Args: cell_elements (list): List of HTML cell elements representing strokes.

        Returns: list[int | None]: Stroke counts per hole, or None if missing.
        """
        # Define empty green in regulation list
        strokes = []

        # Iterate through cell elements
        for cell in cell_elements:
            try:
                # Collect strokes taken from html element
                score_div = cell.find_element(By.CSS_SELECTOR, "div.score-value")
                html = score_div.get_attribute("innerHTML").strip()
                main_value = html.split("<")[0].strip()

            # Handle exception and return n/a if no stroke detected
            except Exception:
                main_value = None

            # Handle empty values
            if not main_value or main_value == "&nbsp;":
                main_value = None

            # Append stroke value to stroke list
            strokes.append(main_value)

        return strokes

    def get_round_date(self) -> date | None:
        """
        Extract the round date.

        Reads the round's date from the scorecard page.

        Returns: date | None: The round date, or None if not found.
        """
        # Collect scorecard date
        try:
            # Find round data element and collect its value
            time_element = self.driver.find_element(By.CSS_SELECTOR, 'p.round-date time')
            datetime_str = time_element.get_attribute('datetime')

            # Strip time from datetime element
            return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ").date()

        # Handle exception if datetime object cannot be found
        except Exception as e:
            self.logger.error(f"Error extracting date: {e}")
            return None

    def get_course_name(self) -> str | None:
        """
        Extract the course name.

        Reads the course name from the scorecard page and normalizes formatting.

        Returns: str | None: Normalized course name, or None if not found.
        """
        # Find course name
        try:
            # Find course name element and collect its value
            course_element = self.driver.find_element(By.CSS_SELECTOR, 'p.course-name')
            course_name = course_element.text.strip()

            # Return value - making sure course name is lower case and white space is handled
            return course_name.lower().replace(" ", "_")

        # Handle exception if course name cannot be found
        except Exception as e:
            self.logger.error(f"Error extracting course name: {e}")
            return None

    def clean_strokes(self, scorecard_data: list) -> list:
        """
        Clean stroke values.

        Replaces invalid or missing stroke entries with numeric values or "N/A".

        Args: scorecard_data (list): Scorecard data with raw strokes.

        Returns: list: Cleaned scorecard data.
        """
        # Iterate through scorecard table
        for hole_data in scorecard_data:

            # Find strokes row
            player_row = hole_data.get(self.vars.round_site_player_name, "")

            # Perform mapping
            match = re.search(r'\d+', str(player_row))
            if match:
                hole_data[self.vars.round_site_player_name] = match.group()
            else:
                hole_data[self.vars.round_site_player_name] = "N/A"

        return scorecard_data

    def convert_player_to_stroke_key(self, scorecard: list[dict]) -> list[dict]:
        """
        Rename player stroke key.

        Moves the player's stroke values to a standardized "Strokes" field.

        Args: scorecard (list[dict]): Scorecard data.

        Returns: list[dict]: Updated scorecard data with "Strokes".
        """
        for hole in scorecard:
            if self.vars.round_site_player_name in hole:
                hole["Strokes"] = hole.pop(self.vars.round_site_player_name)

        return scorecard

    def convert_value(self, val) -> int | float | bool | None | str:
        """
        Convert values to numeric or None.

        Handles conversion to int, float, None, or keeps booleans unchanged.

        Args: val: Raw scorecard value.

        Returns: int | float | bool | None | str: Converted value.
        """
        # Leave booleans unchanged
        if isinstance(val, bool):
            return val

        # Try integers first
        try:
            return int(val)
        except (ValueError, TypeError):
            pass

        # Then floats
        try:
            return float(val)
        except (ValueError, TypeError):
            pass

        # Handle placeholders
        if str(val).strip() in ["N/A", "-"]:
            return None
        return val

    def drop_unplayed_holes(self, data: list[dict]) -> list[dict]:
        """
        Remove unplayed holes.

        Filters out holes with no stroke values.

        Args: data (list[dict]): Scorecard data.

        Returns: list[dict]: Scorecard data with only played holes.
        """
        # Remove unplayed holes from list
        return [d for d in data if d["Strokes"] is not None]

    def parse_scorecard_rows(self, line, scorecard_data) -> dict:
        """
        Parse a row of the scorecard.

        Extracts fairways, GIR, strokes, or generic stats (par, putts, etc.).

        Args: line: Selenium element representing a row of the scorecard.
            scorecard_data (dict): Dictionary to populate with parsed data.

        Returns: dict: Updated scorecard data.
        """
        # Read elements from html
        raw_label = line.find_element(By.CSS_SELECTOR, 'div.line-left > p, div.line-left > p.body-bold')\
            .text.strip()
        label = raw_label.capitalize()

        # Find div values
        cell_elements = line.find_elements(By.CSS_SELECTOR, 'div.values > div.cell, div.values > *')

        # Perform fairways hit mapping
        if 'fairways' in label.lower():
            scorecard_data[label] = self.parse_fairways(cell_elements)

        # Perform greens in regulation mapping
        if 'gir' in label.lower():
            scorecard_data[label] = self.parse_gir(cell_elements)

        # Perform strokes taken mapping
        if self.vars.round_site_player_name.lower() in label.lower():
            scorecard_data[label] = self.parse_strokes(cell_elements)

        # Handle remaining fields
        if label.lower() not in ["fairways", "gir", self.vars.round_site_player_name.lower()]:

            # Default row (Par, Score, Putts, etc.)
            values_elements = line.find_elements(By.CSS_SELECTOR, 'div.values > *')
            values = []
            for el in values_elements:
                text = el.text.strip()
                html = el.get_attribute('innerHTML').strip()
                if not text and html == '&nbsp;':
                    values.append("N/A")
                else:
                    values.append(text or "N/A")

            # Append data to dictionary object
            scorecard_data[label] = values

        return scorecard_data

    def transform_scorecard_data(self, scorecard_data: dict[str, list]) -> list[dict]:
        """
        Transform scorecard structure.

        Converts row-based data into hole-by-hole dictionaries.

        Args: scorecard_data (dict[str, list]): Raw scorecard data by stat type.

        Returns: list[dict]: Structured list of holes with stats.
        """
        holes = []
        num_holes = 18

        for i in range(num_holes):
            hole_data = {"hole": i + 1}

            for key, values in scorecard_data.items():
                if isinstance(values, list) and i < len(values):
                    hole_data[key] = values[i]
                else:
                    hole_data[key] = "N/A"

            holes.append(hole_data)

        return holes

    def annotate_results(self, scorecard: list[dict]) -> list[dict]:
        """
        Annotate hole results.

        Adds a "result" field (e.g., Birdie, Par, Bogey) based on strokes vs par.

        Args: scorecard (list[dict]): Scorecard data with strokes and par.

        Returns: list[dict]: Scorecard with annotated results.
        """
        results = []
        for hole in scorecard:
            strokes = hole.get("Strokes")
            par = hole.get("Par")

            # Handle missing values gracefully
            if strokes is None or par is None:
                hole["result"] = None
                results.append(hole)
                continue

            # Work out hole result
            diff = strokes - par

            # Perform mapping for result
            if diff == -3:
                hole["result"] = "Albatross"
            elif diff == -2:
                hole["result"] = "Eagle"
            elif diff == -1:
                hole["result"] = "Birdie"
            elif diff == 0:
                hole["result"] = "Par"
            elif diff == 1:
                hole["result"] = "Bogey"
            else:
                hole["result"] = "Double Bogey or worse"

            # Append data to result dictionary
            results.append(hole)

        return results

    def collect_scorecard_data(self, url: str) -> tuple[list[dict], str]:
        """
        Collect and process scorecard data from a URL.

        Navigates to a scorecard page, extracts rows, transforms them into hole-level data,
        cleans values, and annotates results.

        Args: url (str): The scorecard page URL.

        Returns: tuple[list[dict], str]: Processed scorecard data and output file name.
        """
        # Define empty scorecard dictionary object
        scorecard_data = {}

        # Navigate to scorecard url and collect round date and course name
        self.driver.get(url)
        round_date = self.get_round_date()
        course_name = self.get_course_name()
        file_name = f'scorecards/{course_name}_{round_date}.json'

        # Collect scorecard data
        scorecard_section = self.driver.find_element(By.CSS_SELECTOR, 'section.round-scorecard')
        round_lines = scorecard_section.find_elements(By.CSS_SELECTOR, 'div.round-line')

        # Iterate through each row in table
        for line in round_lines:

            scorecard_data = self.parse_scorecard_rows(line=line, scorecard_data=scorecard_data)

        # Transform scorecard data
        transformed_scorecard_data = self.transform_scorecard_data(scorecard_data=scorecard_data)

        # Clean stroke data
        transformed_scorecard_data = self.clean_strokes(transformed_scorecard_data)

        transformed_scorecard_data = self.convert_player_to_stroke_key(transformed_scorecard_data)

        # Apply conversion to each entry
        for hole in transformed_scorecard_data:
            for key, value in hole.items():
                hole[key] = self.convert_value(value)

        transformed_scorecard_data = self.drop_unplayed_holes(data=transformed_scorecard_data)

        transformed_scorecard_data = self.annotate_results(scorecard=transformed_scorecard_data)

        return transformed_scorecard_data, file_name
