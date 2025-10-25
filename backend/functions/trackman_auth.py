# Import dependencies
from ..interfaces.data_collection_base import AbstractDataCollection
from selenium.webdriver.support import expected_conditions as EC
from backend.functions.selenium_driver import SeleniumDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from shared import Variables
import logging
import json

class TrackManAuth(AbstractDataCollection, SeleniumDriver):
    """
    Handles authentication and access token retrieval for the TrackMan Golf portal.

    This class provides methods to:
      - Configure and initiate a Selenium WebDriver session.
      - Automate the login process to the TrackMan web portal using stored credentials.
      - Retrieve an API access token required for authenticated requests.

    It inherits from:
        AbstractDataCollection: Base interface for data collection functionality.
        SeleniumDriver: Provides driver configuration and Selenium interaction utilities.

    Typical usage example:
        logger = logging.getLogger(__name__)
        trackman_auth = TrackManAuth(logger, driver_path="chromedriver.exe", headless=True)
        trackman_auth.initiate_driver()
        trackman_auth.login_to_website()
        token = trackman_auth.collect_trackman_access_token()
    """
    def __init__(
        self,
        logger: logging.Logger,
        driver_path: str = 'chromedriver.exe',
        headless: bool = False
    ) -> None:
        """
        Initialize the TrackMan client with Selenium WebDriver and logger.

        Args:
            logger (logging.Logger): Logger instance for logging messages.
            driver_path (str, optional): Path to the ChromeDriver executable. Defaults to 'chromedriver.exe'.
            headless (bool, optional): Whether to run the browser in headless mode. Defaults to False.
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

    def login_to_website(self) -> None:
        """
        Log in to the TrackMan portal using credentials from Variables.

        Raises:
            Exception: If login fails due to any unexpected error.
        """
        try:
            # Navigate the trackman report page
            self.driver.get("https://portal.trackmangolf.com/player/activities?type=reports")

            # Zoom out to load all html components into view
            self.driver.execute_script("document.body.style.zoom='50%'")

            # Enter Password into login form
            WebDriverWait(self.driver, 10) \
                .until(EC.presence_of_element_located((By.ID, 'Email')))
            self.driver.find_element(By.ID, 'Email').send_keys(self.vars.trackman_username)

            # Enter Password into login form
            WebDriverWait(self.driver, 10) \
                .until(EC.presence_of_element_located((By.ID, 'Password')))
            password_field = self.driver.find_element(By.ID, 'Password')
            password_field.send_keys(self.vars.trackman_password)

            # Trigger JavaScript directly to simulate the button click
            self.driver.execute_script("signinBtnClicked()")

        # Handle exception if driver fails to login
        except BaseException:
            self.logger.error('Failed to login to trackman')
            raise

    def collect_trackman_access_token(self) -> str:
        """
        Collect the TrackMan API access token for authenticated requests.

        Returns:
            str: Access token string.

        Raises:
            Exception: If the access token cannot be retrieved.
        """
        # Navigate to authentication url
        self.driver.get("https://portal.trackmangolf.com/api/account/me")

        # Locate the <body> tag and get its inner HTML (content inside the body tag)
        body_content = self.driver.find_element("tag name", "pre").get_attribute("innerHTML")

        # Parse the JSON string
        try:
            # Collect json response
            json_data = json.loads(body_content)

            return json_data['accessToken']

        # Handle exception if driver fails to collect access token
        except BaseException as e:
            self.logger.error(f"Failed to collect trackman access token - {e}")
