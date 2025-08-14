
# Import selenium dependencies
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

# Import project dependencies
from backend.interfaces import AbstractSeleniumDriver

class SeleniumDriver(AbstractSeleniumDriver):
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
