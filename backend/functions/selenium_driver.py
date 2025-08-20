
# Import dependencies
from ..interfaces.selenium_driver_base import AbstractSeleniumDriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

class SeleniumDriver(AbstractSeleniumDriver):
    """
    Provides a Selenium WebDriver configuration utility.

    This class extends `AbstractSeleniumDriver` and is responsible for
    creating and configuring a Chrome WebDriver instance with custom options
    such as headless mode and suppressed logging. It ensures consistent setup
    for browser automation tasks across the project.

    Inherits from:
        AbstractSeleniumDriver: Base class that defines the Selenium driver
        interface/contract to be implemented.
    """
    def configure_driver(
        self,
        driver_path: str = 'chromedriver.exe',
        headless: bool = False,
    ) -> WebDriver:
        """
        Configures and returns a Chrome WebDriver instance.

        This method sets up a Selenium Chrome driver with custom options,
        such as suppressed logging and optional headless mode. The driver
        is maximized on launch to ensure consistent element rendering.

        Args:
            driver_path (str, optional): Path to the ChromeDriver executable.
                Defaults to 'chromedriver.exe'.
            headless (bool, optional): Whether to run the browser in headless mode
                (without a visible UI). Defaults to False.

        Returns:
            WebDriver: A configured instance of Selenium's Chrome WebDriver.

        Raises:
            selenium.common.exceptions.WebDriverException:
                If the WebDriver cannot be started with the given configuration.
        """
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
