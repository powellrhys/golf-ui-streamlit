# Import dependencies
from selenium.webdriver.chrome.webdriver import WebDriver
from abc import ABC, abstractmethod

class AbstractSeleniumDriver(ABC):
    """
    Abstract base class that defines the contract for creating and configuring
    Selenium WebDriver instances.

    Any subclass must implement the `configure_driver` method to ensure a
    consistent setup process (e.g., setting driver paths, enabling headless
    mode, or applying browser-specific options) before returning a usable
    WebDriver object.
    """

    @abstractmethod
    def configure_driver(
        self,
        driver_path: str = 'chromedriver.exe',
        headless: bool = False
    ) -> WebDriver:
        """
        Create and configure a Selenium WebDriver instance.

        This method must be implemented by subclasses to initialize a browser
        driver with custom configuration, such as the executable path and
        whether the browser should run in headless mode.

        Args:
            driver_path (str, optional): Path to the ChromeDriver executable.
                Defaults to 'chromedriver.exe'.
            headless (bool, optional): If True, launches the browser without
                a visible UI. Defaults to False.

        Returns:
            WebDriver: A fully configured Selenium WebDriver instance, ready
            for use in automation tasks.
        """
        pass
