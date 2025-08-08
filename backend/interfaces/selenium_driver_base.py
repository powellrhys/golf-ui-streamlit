# Import python dependencies
from selenium.webdriver.chrome.webdriver import WebDriver
from abc import ABC, abstractmethod

class AbstractSeleniumDriver(ABC):
    """
    Abstract interface for configuring and returning a Selenium WebDriver.
    """
    @abstractmethod
    def configure_driver(
        self,
        driver_path: str = 'chromedriver.exe',
        headless: bool = False
    ) -> WebDriver:
        """
        Configure and return a Selenium WebDriver instance.

        Args:
            driver_path (str): Path to the chromedriver executable.
            headless (bool): Whether to run the browser in headless mode.

        Returns:
            WebDriver: Configured Selenium WebDriver instance.
        """
        pass
