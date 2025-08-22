# Import dependencies
from ..interfaces.data_collection_base import AbstractDataCollection
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from .selenium_driver import SeleniumDriver
from shared import Variables, BlobClient
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException
)
from datetime import datetime, date
from collections import defaultdict
import logging
import re

class RoundData(AbstractDataCollection, SeleniumDriver, BlobClient):
    """
    A data ingestion utility for collecting, parsing, and exporting golf round
    performance data from the Round Site platform.

    This class automates login, navigation, and data extraction using Selenium.
    It retrieves round URLs, scorecards, and performance metrics (fairways,
    greens in regulation, putts, strokes, etc.), transforms the extracted
    scorecard data into structured records, and exports the results to blob
    storage.

    Inherits from:
        AbstractDataCollection: Base interface/contract for data collection
            workflows, ensuring consistency across different data sources.
        SeleniumDriver: Provides Selenium WebDriver configuration and control
            for browser automation.
        BlobClient: Provides blob storage client functionality for exporting
            data to cloud storage.
    """
    def __init__(
        self,
        logger: logging.Logger,
        driver_path: str = 'chromedriver.exe',
        headless: bool = False
    ) -> None:
        """
        Initialize the RoundData object with a logger and Selenium WebDriver.

        Args:
            logger (logging.Logger): Logger instance for recording messages,
                errors, and status updates.
            driver_path (str, optional): Path to the Chrome WebDriver executable.
                Defaults to 'chromedriver.exe'.
            headless (bool, optional): Whether to run Chrome in headless mode
                (no visible browser window). Defaults to False.

        Attributes:
            driver (selenium.webdriver.Chrome): Configured WebDriver instance.
            logger (logging.Logger): Logger used throughout the class.
        """
        super().__init__()
        self.driver = self.configure_driver(driver_path=driver_path, headless=headless)
        self.logger = logger
        self.vars = Variables()

    def login_to_website(self) -> None:
        """
        Automates the login process to the Round Site platform.

        This method navigates to the login page, fills in the username and password
        fields using stored credentials, and submits the login form.

        Steps:
            1. Open the Round Site login page.
            2. Adjust the page zoom level for better rendering.
            3. Populate the email and password fields with credentials stored in
            `self["round_site_username"]` and `self["round_site_password"]`.
            4. Wait until the "Log In" button is clickable and click it.

        Raises:
            selenium.common.exceptions.TimeoutException:
                If the login button does not become clickable within the timeout.
            selenium.common.exceptions.NoSuchElementException:
                If the login fields cannot be found.
            selenium.common.exceptions.WebDriverException:
                For other WebDriver-related errors during the login process.
        """
        # Navigate the trackman report page
        self.driver.get(self.vars.round_site_base_url + "/users/sign_in")

        # Zoom out to load all html components into view
        self.driver.execute_script("document.body.style.zoom='50%'")

        # Iterate through username and password elements and insert values
        for id, var in {"user[email]": "round_site_username", "user[password]": "round_site_password"}.items():

            # Find html element, clear element and insert values
            login_element = self.driver.find_element(By.NAME, id)
            login_element.clear()
            login_element.send_keys(self.vars[var])

        # Find sign in button and click it
        wait = WebDriverWait(self.driver, 10)
        sign_in_button = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            '//button[@type="submit" and normalize-space()="Log In"]'
        )))
        sign_in_button.click()

    def navigate_to_performance_tab(self) -> None:
        """
        Navigates to the "Performance Rounds" tab of the Round Site platform.

        This method directs the Selenium WebDriver to the performance rounds page,
        where round data can be accessed and further processed.

        Raises:
            selenium.common.exceptions.WebDriverException:
                If the navigation request fails (e.g., driver is not initialized or
                the target URL is invalid).
        """
        # Navigate the trackman report page
        self.driver.get(self.vars.round_site_base_url + "/performance/rounds")

    def load_all_round_data(self):
        """
        Iteratively loads all available round data on the performance rounds page.

        This method repeatedly clicks the "Load More" button until no more rounds
        are available. It ensures that all round entries are expanded and visible
        for subsequent parsing.

        Workflow:
            1. Wait for the "Load More" button to become clickable.
            2. Scroll the button into view and click it via JavaScript (to handle
            tricky or partially visible buttons).
            3. Wait until any loading spinner disappears.
            4. Repeat until the button no longer exists or is not clickable.

        Logs:
            - Info message when no more "Load More" buttons are found.
            - Info message if a click is intercepted and retried.

        Raises:
            selenium.common.exceptions.TimeoutException:
                If the "Load More" button or loading spinner does not resolve
                within the timeout.
            selenium.common.exceptions.NoSuchElementException:
                If the button cannot be located.
            selenium.common.exceptions.ElementClickInterceptedException:
                If another element temporarily blocks the click.
        """
        # Define wait component
        wait = WebDriverWait(self.driver, 10)

        # Iterate through all pages and load rounds into view
        while True:
            try:
                # Wait until the button is clickable
                load_more_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.lm-button.button-1")))

                # Scroll into view and click it via JS (safer for tricky buttons)
                self.driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", load_more_button)

                # Optionally wait for loading spinner to disappear
                wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".lm-start.spinner")))

            # Button no longer found or clickable - break the loop
            except (TimeoutException, NoSuchElementException):
                self.logger.info("No more 'Load More' buttons found or clickable.")
                break

            # If something else blocks the click, try scrolling more or wait a bit and retry
            except ElementClickInterceptedException:
                self.logger.info("Click intercepted, retrying after a short wait.")

    def collect_round_urls(self) -> list:
        """
        Collects all round URLs from the performance rounds page.

        This method scans the page for course link elements, extracts the `<a>` tags,
        and gathers their `href` attributes into a list of round URLs.

        Returns:
            list: A list of strings, where each string is the URL to an individual
            round's detail page.

        Raises:
            selenium.common.exceptions.NoSuchElementException:
                If course link elements or their child `<a>` tags cannot be found.
            selenium.common.exceptions.WebDriverException:
                For other driver-related errors during element search.
        """
        # Find all <p> elements with class 'course-link'
        course_link_elements = self.driver.find_elements(By.CSS_SELECTOR, "p.course-link")

        # Define empty round links object
        round_links = []

        # Iterate through each course link and append url to round_links list
        for p_elem in course_link_elements:
            a_tag = p_elem.find_element(By.TAG_NAME, "a")
            href = a_tag.get_attribute("href")
            round_links.append(href)

        return round_links

    def parse_fairways(self, cell_elements) -> list[str]:
        """
        Parses fairway results from scorecard cell elements.

        Each cell is inspected for a "fairway-hit" icon. Based on the icon's CSS
        classes, the method determines whether the shot missed left, hit the
        target, missed right, or is unavailable.

        Args:
            cell_elements (list[selenium.webdriver.remote.webelement.WebElement]):
                A list of scorecard cell elements representing fairway results.

        Returns:
            list[str]: A list of fairway outcomes for each hole. Each entry is one of:
                - "left"   → shot missed left
                - "target" → shot hit the fairway
                - "right"  → shot missed right
                - "N/A"    → data unavailable or element not found

        Notes:
            Falls back to "N/A" if the expected element or class cannot be parsed.
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
                    directions.append('left')
                elif 'target' in classes:
                    directions.append('target')
                elif 'right' in classes:
                    directions.append('right')
                else:
                    directions.append('N/A')
            except BaseException:
                directions.append('N/A')

        return directions

    def parse_gir(self, cell_elements) -> list[bool]:
        """
        Parses Greens in Regulation (GIR) results from scorecard cell elements.

        For each cell, this method checks the element's CSS classes to determine
        whether it represents a successful GIR (on the green in regulation).

        Args:
            cell_elements (list[selenium.webdriver.remote.webelement.WebElement]):
                A list of scorecard cell elements representing GIR results.

        Returns:
            list[bool]: A list of boolean values, where each entry corresponds
            to one hole:
                - True  → hole was a GIR
                - False → hole was not a GIR
        """
        # Define empty green in regulation list
        gir_results = []

        # Iterate through cell elements and declare if green was hit in regulation
        for cell in cell_elements:
            classes = cell.get_attribute('class').split()
            gir_results.append('gir' in classes and 'true' in classes)

        return gir_results

    def get_round_date(self) -> date | None:
        """
        Extracts the round date from the current round page.

        This method locates the `<time>` element inside the round date container,
        retrieves its `datetime` attribute, and parses it into a Python
        `datetime.date` object.

        Returns:
            datetime.date | None: The round date as a `datetime.date` object if
            successfully parsed, otherwise `None`.

        Raises:
            selenium.common.exceptions.NoSuchElementException:
                If the `<time>` element cannot be found.
            ValueError:
                If the datetime string cannot be parsed into a valid date.

        Notes:
            - Expects the `datetime` attribute in ISO 8601 UTC format,
            e.g., `"2025-08-01T17:17:07Z"`.
            - Returns `None` if extraction or parsing fails.
        """
        # Collect scorecard date
        try:
            # Find round data element and collect its value
            time_element = self.driver.find_element(By.CSS_SELECTOR, 'p.round-date time')
            datetime_str = time_element.get_attribute('datetime')

            # Strip time from datetime element
            dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ")

            return dt.date()

        # Handle exception if datetime object cannot be found
        except Exception as e:
            self.logger.error(f"Error extracting date: {e}")
            return None

    def get_course_name(self) -> str | None:
        """
        Extracts the course name from the current round page.

        This method retrieves the course name text, normalizes it to lowercase,
        and replaces spaces with underscores for use in filenames or identifiers.

        Returns:
            str | None: The normalized course name (e.g., "pebble_beach") if
            successfully extracted, otherwise `None`.

        Raises:
            selenium.common.exceptions.NoSuchElementException:
                If the course name element cannot be found.
            selenium.common.exceptions.WebDriverException:
                For other driver-related errors during element search.

        Notes:
            - Normalization makes the string safe for use in filenames.
            - Falls back to `None` if extraction or parsing fails.
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
        Cleans the strokes field for the tracked player in each hole's scorecard data.

        This method ensures that only the first numeric value is retained in the
        player's strokes entry (useful if the raw data includes extra symbols or text).

        Args:
            scorecard_data (list[dict]): A list of dictionaries, each representing
                one hole's data. The tracked player's strokes are stored under the
                key defined by `self.vars.round_site_player_name`.

        Returns:
            list[dict]: The updated scorecard data with cleaned stroke values for
            the tracked player. Each value will be:
                - A stringified integer if a number is found.
                - `"N/A"` if no numeric value is present.
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

    def collect_scorecard_data(self, round_links: list[str]) -> dict:
        """
        Collects and processes scorecard data for multiple rounds.

        For each round URL:
            1. Loads the round page.
            2. Extracts the round date and course name.
            3. Parses scorecard rows (fairways, GIR, par, score, putts, etc.).
            4. Transforms the raw scorecard data into a per-hole structure.
            5. Cleans the stroke values for the configured player.
            6. Exports the processed scorecard data to blob storage as JSON.

        Args:
            round_links (list[str]): A list of round page URLs to process.

        Returns:
            dict: A dictionary containing the last processed round's raw scorecard
            data (prior to transformation and cleaning). Exported data is written
            to blob storage for all rounds.

        Raises:
            selenium.common.exceptions.NoSuchElementException:
                If expected scorecard elements cannot be found.
            selenium.common.exceptions.WebDriverException:
                For other driver-related errors during navigation or scraping.
            Exception:
                Any other unexpected errors during ingestion are logged and skipped.

        Notes:
            - Data for each round is saved in blob storage under:
            `scorecards/{course}_{date}.json`
            - Logs progress and errors using the provided logger.
        """
        # Define empty scorecard dictionary object
        scorecard_data = {}

        # Iterate through each round link
        for index, url in enumerate(round_links, start=1):

            # Collect scorecard data
            try:
                # Navigate to scorecard url and collect round date and course name
                self.driver.get(url)
                date = self.get_round_date()
                course = self.get_course_name()

                # Log iteration progress
                self.logger.info(f"Evaluating scorecard {index} of {len(round_links)}: "
                                 f"{course.capitalize().replace('_', ' ')} | {date}")

                # Collect scorecard data
                scorecard_section = self.driver.find_element(By.CSS_SELECTOR, 'section.round-scorecard')
                round_lines = scorecard_section.find_elements(By.CSS_SELECTOR, 'div.round-line')

                # Iterate through each row in table
                for line in round_lines:
                    raw_label = line.find_element(By.CSS_SELECTOR, 'div.line-left > p, div.line-left > p.body-bold')\
                        .text.strip()
                    label = raw_label.capitalize()

                    # Find div values
                    cell_elements = line.find_elements(By.CSS_SELECTOR, 'div.values > div.cell')

                    # Perform fairways hit mapping
                    if 'fairways' in label.lower():
                        scorecard_data[label] = self.parse_fairways(cell_elements)
                        continue

                    # Perform greens in regulation mapping
                    if 'gir' in label.lower():
                        scorecard_data[label] = self.parse_gir(cell_elements)
                        continue

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

                # Transform scorecard data
                transformed_scorecard_data = self.transform_scorecard_data(scorecard_data=scorecard_data)

                # Clean stroke data
                transformed_scorecard_data = self.clean_strokes(transformed_scorecard_data)

                # Export scorecard data to blob storage
                self.export_dict_to_blob(
                    data=transformed_scorecard_data,
                    container='golf',
                    output_filename=f'scorecards/{course}_{date}.json')

            # Handle exception and log error
            except BaseException as e:
                self.logger.error(f"Failed to ingest scorecard \n - {e}")

    def transform_scorecard_data(self, scorecard_data: dict[str, list]) -> list[dict]:
        """
        Transforms raw scorecard data into a per-hole structured format.

        This method takes the raw scorecard dictionary (where each key maps
        to a list of values across 18 holes) and restructures it into a list
        of dictionaries, where each dictionary represents a single hole with
        its associated metrics.

        Args:
            scorecard_data (dict[str, list]): A dictionary where:
                - Keys are metric labels (e.g., "Par", "Score", "Putts",
                "Fairways", "GIR").
                - Values are lists of length 18 (one entry per hole).

        Returns:
            list[dict]: A list of 18 dictionaries, each containing:
                - "hole" (int): Hole number (1-18).
                - One key/value pair per metric extracted from `scorecard_data`.
                - Defaults to "N/A" if a metric has fewer than 18 values.

        Notes:
            - Assumes standard 18-hole rounds.
            - Provides defensive handling for incomplete data lists.
        """
        # Define empty hole dictionary
        holes = []

        # Assuming all lists have exactly 18 elements
        num_holes = 18

        # Iterate through each hole on course
        for i in range(num_holes):

            # Hole number from 1 to 18
            hole_data = {"hole": i + 1}

            # Add each key/value from scorecard_data for the current hole index
            for key, values in scorecard_data.items():
                # Defensive: If value list shorter than 18, use 'N/A' or suitable default
                if i < len(values):
                    hole_data[key] = values[i]
                else:
                    hole_data[key] = "N/A"

            # Append data to holes list
            holes.append(hole_data)

        return holes


class RoundAggregator(BlobClient):
    """
    Aggregates and restructures golf round data from blob storage.

    This class loads multiple JSON scorecard files (each representing a full
    round), merges them, and produces aggregated per-hole statistics for a
    given course. The aggregated data can then be exported back to blob
    storage for downstream analysis or reporting.

    Inherits from:
        BlobClient: Provides blob storage functionality for reading and
            writing JSON scorecard files.
        Variables: Provides access to configuration variables such as
            container names, course identifiers, or player names.
    """
    def __init__(self, logger: logging.Logger):
        """
        Initialize the RoundAggregator with logging support.

        Args:
            logger (logging.Logger): Logger instance for recording progress,
                debug information, and error messages.

        Attributes:
            logger (logging.Logger): Used throughout the class for logging.
        """
        super().__init__()
        self.logger = logger
        self.vars = Variables()

    def aggregate_holes_by_course(self) -> None:
        """
        Aggregates per-hole data across multiple rounds for a specific course.

        This method scans all JSON scorecard files in blob storage, filters them
        for the current course, groups hole-level data by hole number, attaches
        the round date to each record, sorts the results by date (most recent first),
        and exports a JSON summary file per hole.

        Workflow:
            1. List all JSON scorecard files from blob storage.
            2. Filter by the configured course name.
            3. Extract the round date from each filename.
            4. Load the round data and group hole-level stats by hole number.
            5. Append the round date to each hole's data.
            6. Sort per-hole data by date (descending).
            7. Export per-hole aggregated data back to blob storage.

        Blob Output:
            - Each hole's data is written as a JSON file under:
            `{course_name}_golf_course_hole_summary/hole_{n}.json`

        Raises:
            Exception: Any unexpected errors during blob reading/writing
            are logged, but processing continues.
        """
        # Define blob directory name
        directory_path = "scorecards"

        # Define hole data map and iterate through each file in blob container
        hole_data_map = defaultdict(list)
        for filename in self.list_blob_filenames(container_name="golf", directory_path=directory_path):

            # Make sure container file is a json file and has the course of interest in the name
            if filename.lower().endswith(".json") and self.vars.golf_course_name.lower() in filename.lower():

                # Extract date from filename using regex
                match = re.search(r"(\d{4}-\d{2}-\d{2})\.json$", filename)
                if not match:
                    self.logger.info(f"Skipping file with unexpected format: {filename}")
                    continue

                # Read file from blob storage
                file_date = match.group(1)
                try:
                    round_data = self.read_blob_to_dict(container="golf", input_filename=filename)

                # Handle exception if file could not be read
                except Exception as e:
                    self.logger.error(f"Error reading {filename}: {e}")
                    continue

                # Iterate through each hole and append data to hole data map
                for hole in round_data:
                    hole_number = hole.get("hole")
                    if hole_number:
                        hole_with_date = dict(hole)
                        hole_with_date["date"] = file_date
                        hole_data_map[hole_number].append(hole_with_date)

        # Save each hole’s data sorted by date (most recent first)
        for index, (hole_num, hole_list) in enumerate(hole_data_map.items(), start=1):

            # Log progress and sort data by mmost recent datetime
            self.logger.info(f"{index}/{len(hole_data_map)} - Aggregating data for hole {hole_num}")
            sorted_holes = sorted(
                hole_list,
                key=lambda h: datetime.strptime(h["date"], "%Y-%m-%d"),
                reverse=True
            )

            # Export aggregated data to blob
            self.export_dict_to_blob(
                data=sorted_holes,
                container='golf',
                output_filename=f'{self.vars.golf_course_name}_golf_course_hole_summary/hole_{hole_num}.json')
