# Import dependencies
from selenium.webdriver.common.by import By
from .selenium_driver import SeleniumDriver
from shared import Variables, BlobClient
from datetime import datetime, date
import logging
import re

class ScorecardParser(SeleniumDriver, BlobClient):
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
        directions = []

        for cell in cell_elements:
            try:
                img = cell.find_element(By.CSS_SELECTOR, 'img')
                alt = img.get_attribute('alt').lower()
                if 'target' in alt:
                    directions.append('Target')
                elif 'right' in alt:
                    directions.append('Right')
                elif 'left' in alt:
                    directions.append('Left')
                else:
                    directions.append('N/A')
            except Exception:
                directions.append('N/A')

        return directions

    def parse_gir(self, cell_elements: list) -> list[bool]:
        """
        Parse greens in regulation (GIR).

        Determines whether the green was reached in regulation for each hole.

        Args: cell_elements (list): List of HTML cell elements representing GIR data.

        Returns: list[bool]: True if GIR, False otherwise per hole.
        """
        gir_results = []

        for cell in cell_elements:
            try:
                cell.find_element(By.CSS_SELECTOR, 'img[alt="greenHit"]')
                gir_results.append(True)
            except Exception:
                gir_results.append(False)

        return gir_results

    def parse_strokes(self, cell_elements: list) -> list[int | None]:
        """
        Parse stroke counts.

        Extracts the number of strokes taken per hole from scorecard cells.

        Args: cell_elements (list): List of HTML cell elements representing strokes.

        Returns: list[int | None]: Stroke counts per hole, or None if missing.
        """
        strokes = []

        for cell in cell_elements:
            try:
                span = cell.find_element(By.CSS_SELECTOR, 'span > span > span')
                value = span.text.strip()
                strokes.append(value if value else None)
            except Exception:
                strokes.append(None)

        return strokes

    def get_round_date(self) -> date | None:
        """
        Extract the round date.

        Reads the round's date from the scorecard page.

        Returns: date | None: The round date, or None if not found.
        """
        try:
            date_element = self.driver.find_element(By.CSS_SELECTOR, 'section.round-details p')
            date_str = date_element.text.strip()

            return datetime.strptime(date_str, "%d/%m/%Y").date()

        except Exception as e:
            self.logger.error(f"Error extracting date: {e}")
            return None

    def get_course_name(self) -> str | None:
        """
        Extract the course name.

        Reads the course name from the scorecard page and normalizes formatting.

        Returns: str | None: Normalized course name, or None if not found.
        """
        try:
            course_element = self.driver.find_element(By.CSS_SELECTOR, 'section.round-details p:nth-of-type(2)')
            course_name = course_element.text.strip()

            return course_name.lower().replace(" ", "_")

        except Exception as e:
            self.logger.error(f"Error extracting course name: {e}")
            return None

    def clean_strokes(self, scorecard_data: list) -> list:
        """
        Clean stroke values.

        Replaces invalid or missing stroke entries with numeric values or "N/A".
        Falls back to extracting the first number from the 'Scores' field if the
        player name key is missing or unpopulated.

        Args: scorecard_data (list): Scorecard data with raw strokes.

        Returns: list: Cleaned scorecard data.
        """
        for hole_data in scorecard_data:
            player_row = hole_data.get(self.vars.round_site_player_name, "")

            # If player name key is empty/missing, fall back to the Scores field
            if not player_row or player_row == "N/A":
                player_row = hole_data.get("Scores", "")

            # Extract the first integer (the gross score, ignoring the +/-1 suffix)
            match = re.search(r'^\d+', str(player_row).strip())
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
        if isinstance(val, bool):
            return val

        try:
            return int(val)
        except (ValueError, TypeError):
            pass

        try:
            return float(val)
        except (ValueError, TypeError):
            pass

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
        return [d for d in data if d["Strokes"] is not None]

    def parse_scorecard_rows(self, line, scorecard_data) -> dict:
        """
        Parse a row of the scorecard.

        Extracts fairways, GIR, strokes, or generic stats (par, putts, etc.).

        Args: line: Selenium element representing a row of the scorecard.
            scorecard_data (dict): Dictionary to populate with parsed data.

        Returns: dict: Updated scorecard data.
        """
        # Get row label from the sticky first cell
        try:
            raw_label = line.find_element(By.CSS_SELECTOR, 'div.sticky span.truncate').text.strip()
        except Exception:
            return scorecard_data

        # Skip header row (hole numbers) and empty labels
        if not raw_label:
            return scorecard_data

        label = raw_label.capitalize()

        # Get hole cells only — direct children, excluding the sticky label cell
        # and OUT/IN/TOTAL summary cells (identified by shrink-0)
        all_cells = line.find_elements(By.XPATH, './div')
        hole_cells = [
            c for c in all_cells
            if 'sticky' not in (c.get_attribute('class') or '') and 'shrink-0' not in (c.get_attribute('class') or '')
        ]

        if 'fairways' in label.lower():
            scorecard_data[label] = self.parse_fairways(hole_cells)

        elif 'gir' in label.lower():
            scorecard_data[label] = self.parse_gir(hole_cells)

        elif self.vars.round_site_player_name.lower() in label.lower():
            scorecard_data[label] = self.parse_strokes(hole_cells)

        else:
            values = []
            for cell in hole_cells:
                text = cell.text.strip()
                values.append(text if text else 'N/A')
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
                # rename key "S.i." to "S. index"
                new_key = "S. index" if key == "S.i." else key
                if isinstance(values, list) and i < len(values):
                    hole_data[new_key] = values[i]
                else:
                    hole_data[new_key] = "N/A"

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

            if strokes is None or par is None:
                hole["result"] = None
                results.append(hole)
                continue

            diff = strokes - par

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

            results.append(hole)

        return results

    def identify_new_data(self, scorecard_urls: list) -> list:
        """
        Identify new Hole19 scorecards that are not yet stored in blob storage.

        Extracts scorecard IDs from the provided URLs, compares them with IDs of
        scorecards already saved in the "golf/scorecards" container, and returns
        the URLs of scorecards that are new.

        Args:
            scorecard_urls (list): List of Hole19 scorecard URLs to check.

        Returns:
            list: List of scorecard URLs corresponding to new scorecards not yet collected.
        """
        scorecard_ids = [url.split("/")[-1] for url in scorecard_urls]

        collected_scorecard = self.list_blob_filenames(container_name="golf", directory_path="scorecards")

        collected_scorecard_ids = [file.split("_")[-1].replace(".json", "") for file in collected_scorecard]

        return [f"https://www.hole19golf.com/performance/rounds/{id}"
                for id in list(set(scorecard_ids) - set(collected_scorecard_ids))]

    def collect_scorecard_data(self, url: str) -> tuple[list[dict], str]:
        """
        Collect and process scorecard data from a URL.

        Navigates to a scorecard page, extracts rows, transforms them into hole-level data,
        cleans values, and annotates results.

        Args: url (str): The scorecard page URL.

        Returns: tuple[list[dict], str]: Processed scorecard data and output file name.
        """
        scorecard_data = {}

        self.driver.get(url)
        round_date = self.get_round_date()
        course_name = self.get_course_name()
        file_name = f'scorecards/{course_name}_{round_date}_{url.split("/")[-1]}.json'

        scorecard_section = self.driver.find_element(By.CSS_SELECTOR, 'section.round-scorecard')

        scorecard_grid = scorecard_section.find_element(By.CSS_SELECTOR, 'section.grid')

        round_lines = scorecard_grid.find_elements(By.CSS_SELECTOR, 'div.contents')

        for line in round_lines:
            scorecard_data = self.parse_scorecard_rows(line=line, scorecard_data=scorecard_data)

        transformed_scorecard_data = self.transform_scorecard_data(scorecard_data=scorecard_data)

        transformed_scorecard_data = self.clean_strokes(transformed_scorecard_data)

        transformed_scorecard_data = self.convert_player_to_stroke_key(transformed_scorecard_data)

        for hole in transformed_scorecard_data:
            for key, value in hole.items():
                hole[key] = self.convert_value(value)

        transformed_scorecard_data = self.drop_unplayed_holes(data=transformed_scorecard_data)

        transformed_scorecard_data = self.annotate_results(scorecard=transformed_scorecard_data)

        return transformed_scorecard_data, file_name
