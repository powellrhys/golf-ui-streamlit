# Import python dependencies
from abc import ABC, abstractmethod

class AbstractDataCollection(ABC):
    """
    """
    @abstractmethod
    def login_to_website(self) -> None:
        pass
