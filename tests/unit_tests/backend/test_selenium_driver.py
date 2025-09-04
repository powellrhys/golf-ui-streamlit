# Import dependencies
from unittest.mock import patch, MagicMock
from backend import SeleniumDriver

class TestSeleniumDriver:
    """
    Unit tests for SeleniumDriver.configure_driver.

    These tests use unittest.mock to patch out the real Selenium WebDriver
    so no actual browser is launched during test execution.
    """

    @patch("backend.functions.selenium_driver.webdriver.Chrome")
    def test_configure_driver_default(self, mock_chrome):
        """
        Default behavior: should create a Chrome driver instance,
        maximize the window, and return the driver.
        """
        # Create a fake driver object
        mock_driver = MagicMock()

        # Make webdriver.Chrome() return the fake driver instead of a real one
        mock_chrome.return_value = mock_driver

        # Call the method under test
        driver = SeleniumDriver().configure_driver()

        # The returned object should be the fake driver
        assert driver == mock_driver

        # webdriver.Chrome should have been called exactly once
        mock_chrome.assert_called_once()

        # The driver window should have been maximized
        driver.maximize_window.assert_called_once()

    @patch("backend.functions.selenium_driver.webdriver.Chrome")
    def test_configure_driver_headless(self, mock_chrome):
        """
        Headless mode: should add the '--headless' option when
        creating the Chrome driver.
        """
        # Create a fake driver object
        mock_driver = MagicMock()

        # Make webdriver.Chrome() return the fake driver
        mock_chrome.return_value = mock_driver

        # Call the method under test with headless=True
        SeleniumDriver().configure_driver(headless=True)

        # Inspect the arguments that webdriver.Chrome was called with
        _, kwargs = mock_chrome.call_args
        options = kwargs["options"]

        # Verify that '--headless' was included in the Chrome options
        assert "--headless" in options.arguments
