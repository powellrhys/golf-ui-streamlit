# Import dependencies
from abc import ABC, abstractmethod

class AbstractDataCollection(ABC):
    """
    Abstract base class for data collection processes.

    This class defines the blueprint for initializing a driver and
    logging into a website. Subclasses must implement these methods
    according to the specific website or driver being used.
    """
    @abstractmethod
    def initiate_driver(self) -> None:
        """
        Initialize the web driver instance.

        This method should set up and configure the web driver
        (e.g., Selenium, Playwright, etc.) that will be used
        to interact with the website.

        Raises:
            RuntimeError: If the driver could not be initialized.
        """
        pass

    @abstractmethod
    def login_to_website(self) -> None:
        """
        Log in to the target website.

        This method should handle the authentication flow required
        to access the website. Implementation may vary depending
        on the website's login process.

        Raises:
            ValueError: If login credentials are invalid.
            ConnectionError: If the website cannot be reached.
        """
        pass
