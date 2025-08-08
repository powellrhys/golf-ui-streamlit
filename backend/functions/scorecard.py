# Install python dependencies
from collections import defaultdict
from datetime import datetime
import logging
import re

# Import selenium dependencies
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

# Import project dependencies
from backend.functions.selenium_driver import SeleniumDriver
from backend.functions.blob_client import BlobClient
from shared import Variables


class RoundData(SeleniumDriver, BlobClient):
    """
    """
    def __init__(
        self,
        logger: logging.Logger,
        driver_path: str = 'chromedriver.exe',
        headless: bool = False
    ) -> None:
        """
        """
        super().__init__()
        self.driver = self.configure_driver(driver_path=driver_path, headless=headless)
        self.logger = logger

    def login_to_round_site(self) -> None:
        """
        """
        # Navigate the trackman report page
        self.driver.get(self.round_site_base_url + "/users/sign_in")

        self.driver.execute_script("document.body.style.zoom='50%'")

        for id, var in {"user[email]": "round_site_username", "user[password]": "round_site_password"}.items():

            login_element = self.driver.find_element(By.NAME, id)
            login_element.clear()
            login_element.send_keys(self[var])

        wait = WebDriverWait(self.driver, 10)
        sign_in_button = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            '//button[@type="submit" and normalize-space()="Log In"]'
        )))
        sign_in_button.click()

    def navigate_to_performance_tab(self) -> None:
        """
        """
        # Navigate the trackman report page
        self.driver.get(self.round_site_base_url + "/performance/rounds")

    def load_all_round_data(self):
        """
        """
        wait = WebDriverWait(self.driver, 10)

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

    def collect_round_urls(
        self,
    ) -> list:
        """
        """
        # Find all <p> elements with class 'course-link'
        course_link_elements = self.driver.find_elements(By.CSS_SELECTOR, "p.course-link")

        round_links = []
        for p_elem in course_link_elements:
            a_tag = p_elem.find_element(By.TAG_NAME, "a")
            href = a_tag.get_attribute("href")
            round_links.append(href)

        return round_links

    def parse_fairways(self, cell_elements):
        directions = []
        for cell in cell_elements:
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

    def parse_gir(self, cell_elements):
        gir_results = []
        for cell in cell_elements:
            classes = cell.get_attribute('class').split()
            gir_results.append('gir' in classes and 'true' in classes)
        return gir_results

    def get_round_date(self) -> datetime.date:
        """
        Extracts the round date as a Python date object (YYYY-MM-DD).
        """
        try:
            time_element = self.driver.find_element(By.CSS_SELECTOR, 'p.round-date time')
            datetime_str = time_element.get_attribute('datetime')  # e.g., '2025-08-01T17:17:07Z'
            dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ")
            return dt.date()
        except Exception as e:
            print(f"Error extracting date: {e}")
            return None  # or use datetime.date.min if you prefer a default

    def get_course_name(self) -> str:
        """
        Extracts the course name from the round page.

        Returns:
            str: Course name, or None if extraction fails.
        """
        try:
            course_element = self.driver.find_element(By.CSS_SELECTOR, 'p.course-name')
            course_name = course_element.text.strip()
            return course_name.lower().replace(" ", "_")
        except Exception as e:
            print(f"Error extracting course name: {e}")
            return None

    def clean_strokes(self, scorecard_data: list) -> list:
        """
        Cleans the 'Rhys' field in each hole's data by extracting only the first number (int or str).

        Args:
            scorecard_data (list): List of dicts, each representing one hole's data.

        Returns:
            list: Updated scorecard_data with cleaned 'Rhys' values.
        """
        import re

        for hole_data in scorecard_data:
            rhys_raw = hole_data.get("Rhys", "")

            # Find the first number in the string (can be 1 or 2 digits)
            match = re.search(r'\d+', str(rhys_raw))
            if match:
                hole_data["Rhys"] = match.group()
            else:
                hole_data["Rhys"] = "N/A"  # or None, or 0, depending on your preference

        return scorecard_data

    def collect_scorecard_data(self, round_links: list) -> dict:
        url = round_links[0]
        scorecard_data = {}

        for index, url in enumerate(round_links, start=1):

            try:
                self.driver.get(url)
                date = self.get_round_date()
                course = self.get_course_name()

                self.logger.info(f"Evaluating scorecard {index} of {len(round_links)}: "
                                 f"{course.capitalize().replace("_", " ")} | {date}")

                scorecard_section = self.driver.find_element(By.CSS_SELECTOR, 'section.round-scorecard')
                round_lines = scorecard_section.find_elements(By.CSS_SELECTOR, 'div.round-line')

                for line in round_lines:
                    raw_label = line.find_element(By.CSS_SELECTOR, 'div.line-left > p, div.line-left > p.body-bold')\
                        .text.strip()
                    label = raw_label.capitalize()

                    cell_elements = line.find_elements(By.CSS_SELECTOR, 'div.values > div.cell')

                    if 'fairways' in label.lower():
                        scorecard_data[label] = self.parse_fairways(cell_elements)
                        continue

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

                    scorecard_data[label] = values

                transformed_scorecard_data = self.transform_scorecard_data(scorecard_data=scorecard_data)
                transformed_scorecard_data = self.clean_strokes(transformed_scorecard_data)

                self.export_dict_to_blob(
                    data=transformed_scorecard_data,
                    container='golf',
                    output_filename=f'scorecards/{course}_{date}.json')

            except BaseException as e:
                self.logger.error(f"Failed to ingest scorecard \n - {e}")

    def transform_scorecard_data(self, scorecard_data):
        holes = []

        # Assuming all lists have exactly 18 elements
        num_holes = 18

        for i in range(num_holes):
            hole_data = {"hole": i + 1}  # Hole number from 1 to 18

            # Add each key/value from scorecard_data for the current hole index
            for key, values in scorecard_data.items():
                # Defensive: If value list shorter than 18, use 'N/A' or suitable default
                if i < len(values):
                    hole_data[key] = values[i]
                else:
                    hole_data[key] = "N/A"

            holes.append(hole_data)

        return holes


class RoundAggregator(BlobClient, Variables):
    """
    Aggregates hole-level stats from multiple JSON files
    into per-hole JSON files for a given course.
    """
    def __init__(self, logger: logging.Logger):
        super().__init__()
        self.logger = logger

    def aggregate_holes_by_course(
        self,
    ):
        """
        """

        directory_path = "scorecards"
        hole_data_map = defaultdict(list)
        for filename in self.list_blob_filenames(container_name="golf", directory_path=directory_path):

            if filename.lower().endswith(".json") and self.golf_course_name.lower() in filename.lower():

                # Extract date from filename using regex
                match = re.search(r"(\d{4}-\d{2}-\d{2})\.json$", filename)
                if not match:
                    self.logger.info(f"Skipping file with unexpected format: {filename}")
                    continue

                file_date = match.group(1)

                try:
                    round_data = self.read_blob_to_dict(container="golf", input_filename=filename)
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
                    continue

                for hole in round_data:
                    hole_number = hole.get("hole")
                    if hole_number:
                        hole_with_date = dict(hole)
                        hole_with_date["date"] = file_date
                        hole_data_map[hole_number].append(hole_with_date)

        # Save each hole’s data sorted by date (most recent first)
        for index, (hole_num, hole_list) in enumerate(hole_data_map.items(), start=1):

            self.logger.info(f"{index}/{len(hole_data_map)} - Aggregating data for hole {hole_num}")
            sorted_holes = sorted(
                hole_list,
                key=lambda h: datetime.strptime(h["date"], "%Y-%m-%d"),
                reverse=True
            )

            self.export_dict_to_blob(
                data=sorted_holes,
                container='golf',
                output_filename=f'{self.golf_course_name}_golf_course_hole_summary/hole_{hole_num}.json')
