# Install python dependencies
from dotenv import load_dotenv
import logging
import os

# Import selenium dependencies
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver


load_dotenv()

class Variables:
    """
    """
    def __init__(self):
        self.round_site_base_url = os.getenv("round_site_base_url")
        self.round_site_username = os.getenv("round_site_username")
        self.round_site_password = os.getenv("round_site_password")

    def __getitem__(self, key):
        return getattr(self, key)

class SeleniumDriver:
    """
    """
    def configure_driver(
        self,
        driver_path: str = 'chromedriver.exe',
        headless: bool = False,
    ) -> WebDriver:
        '''
        Decorator that logs the execution of a function.

        This decorator retrieves a logger from the function's keyword arguments (if provided),
        logs the function's execution start, and logs either a success or failure message
        upon completion or exception.

        Args:
            func (Callable): The function to be decorated.

        Returns:
            Callable: The wrapped function with logging functionality.

        Raises:
            BaseException: If the decorated function raises an exception, it is logged and re-raised.
        '''
        # Configure logging to suppress unwanted messages
        chrome_options = Options()
        chrome_options.add_argument("--log-level=3")

        # If headless declared, activate headless mode
        if headless:
            chrome_options.add_argument("--headless")

        # Configure Driver with options
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.maximize_window()

        return driver

class RoundData(SeleniumDriver):
    """
    """
    def __init__(self,
                 logger: logging.Logger,
                 driver_path: str = 'chromedriver.exe',
                 headless: bool = False):
        """
        """
        self.driver = self.configure_driver(driver_path=driver_path, headless=headless)
        self.vars = Variables()
        self.logger = logger

    def login_to_round_site(self) -> None:
        """
        """
        # Navigate the trackman report page
        self.driver.get(self.vars.round_site_base_url + "/users/sign_in")

        self.driver.execute_script("document.body.style.zoom='50%'")

        for id, var in {"user_email": "round_site_username", "user_password": "round_site_password"}.items():
            login_element = self.driver.find_element(By.ID, id)
            login_element.clear()
            login_element.send_keys(self.vars[var])

        wait = WebDriverWait(self.driver, 10)
        sign_in_button = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                '//input[@type="submit" and @value="Sign in"]')))
        sign_in_button.click()

    def navigate_to_performance_tab(self) -> None:
        """
        """
        # Navigate the trackman report page
        self.driver.get(self.vars.round_site_base_url + "/performance/rounds")

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
        
    def collect_scorecard_data(self, round_links: list) -> None:
        """
        Loads a live scorecard URL and extracts structured golf data.
        """
        url = round_links[0]

        try:
            self.driver.get(url)

            import time
            time.sleep(3)  # wait for page to load fully; consider WebDriverWait for more reliable waits

            scorecard_section = self.driver.find_element(By.CSS_SELECTOR, 'section.round-scorecard')
            round_lines = scorecard_section.find_elements(By.CSS_SELECTOR, 'div.round-line')

            for line in round_lines:
                label = line.find_element(By.CSS_SELECTOR, 'div.line-left > p, div.line-left > p.body-bold').text

                if 'fairways' in label.lower():
                    fairway_elements = line.find_elements(By.CSS_SELECTOR, 'div.fairway-hit.scorecard-icon')
                    directions = []

                    for el in fairway_elements:
                        classes = el.get_attribute('class').split()
                        if 'left' in classes:
                            directions.append('left')
                        elif 'target' in classes:
                            directions.append('target')
                        elif 'right' in classes:
                            directions.append('right')
                        else:
                            directions.append('unknown')

                    print(f"{label}:")
                    print("Directions:", directions)
                    print("-" * 40)
                    continue

                # Extract values, ignoring cells that are empty or contain just &nbsp;
                values_elements = line.find_elements(By.CSS_SELECTOR, 'div.values > *')
                values = []
                for el in values_elements:
                    text = el.text.strip()
                    # Also check if the element's HTML contains only &nbsp; or is empty
                    html = el.get_attribute('innerHTML').strip()
                    if text and text != '\xa0' and html != '&nbsp;':
                        values.append(text)

                # Extract points similarly
                points_elements = line.find_elements(By.CSS_SELECTOR, 'div.points > *')
                points = []
                for p in points_elements:
                    text = p.text.strip()
                    html = p.get_attribute('innerHTML').strip()
                    if text and text != '\xa0' and html != '&nbsp;':
                        points.append(text)

                print(f"{label}:")
                print("Values:", values)
                if points:
                    print("Points:", points)
                print("-" * 40)

        finally:
            self.driver.quit()