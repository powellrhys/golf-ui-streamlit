# Import dependencies
from abc import ABC, abstractmethod

class AbstractDataCollection(ABC):
    """
    Abstract base class for data collection workflows.

    This class defines the interface for any data collection implementation.
    Subclasses must implement methods for authenticating and retrieving data
    from their respective sources (e.g., websites, APIs).

    Inherits from:
        ABC: Python's Abstract Base Class, ensuring subclasses implement
        required abstract methods.
    """
    @abstractmethod
    def initiate_driver(self) -> None:
        """
        """
        pass

    @abstractmethod
    def login_to_website(self) -> None:
        """
        Abstract method for handling website login.

        Subclasses must implement this method to define how authentication
        is performed against their target website.

        Raises:
            NotImplementedError: If called directly on the abstract class
            without an implementation in a subclass.
        """
        pass
