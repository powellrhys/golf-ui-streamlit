# Import dependencies
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, TimeoutException
from ..interfaces.data_collection_base import AbstractDataCollection
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from .selenium_driver import SeleniumDriver
from shared import Variables
import logging

class Hole19Navigator(AbstractDataCollection, SeleniumDriver):
    """
    Automates navigation and data collection from the Hole19 website.

    Uses Selenium to log in, load performance data, and extract round URLs
    for further processing.
    """
    def __init__(self, logger: logging.Logger,
                 driver_path: str = 'chromedriver.exe',
                 headless: bool = False) -> None:
        """
        Initialize the Hole19Navigator.

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

        Args: None

        Returns: None
        """
        self.driver = self.configure_driver(driver_path=self.driver_path, headless=self.headless)

    def login_to_website(self) -> None:
        """
        Log into the Hole19 website.

        Opens the login page, enters stored credentials, and clicks the login button.

        Args: None

        Returns: None

        Raises:
            TimeoutException: If the login button cannot be clicked within the wait time.
            NoSuchElementException: If login form fields are not found.
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
        Navigate to the performance rounds page.

        Directs the WebDriver to the Hole19 performance rounds section.

        Args: None

        Returns: None
        """
        # Navigate the trackman report page
        self.driver.get(self.vars.round_site_base_url + "/performance/rounds")

    def load_all_hole19_rounds(self):
        """
        Load all available rounds.

        Continuously clicks the 'Load More' button until no further rounds are available.

        Args: None

        Returns: None

        Raises:
            ElementClickInterceptedException: If a click attempt is blocked by another element.
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
        Collect all round URLs.

        Extracts links from the performance rounds page and returns them as a list.

        Args: None

        Returns: list: A list of round URLs extracted from the page.
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
