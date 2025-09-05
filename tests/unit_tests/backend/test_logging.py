# Import dependencies
from backend import configure_logging
import warnings
import logging

class TestConfigureLogging:
    """
    Unit tests for configure_logging() utility.

    Ensures the logger is configured correctly with name, level,
    formatter, and warning suppression.
    """

    def setup_method(self):
        """
        Reset warning filters and remove any BASIC logger handlers
        before each test to avoid side effects.
        """
        # Reset warnings
        warnings.resetwarnings()

        # Removing all existing loggers
        logger = logging.getLogger('BASIC')
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    def test_returns_logger_instance(self):
        """
        Should return a logging.Logger instance.
        """
        # Create logger and make sure it is the correct type
        logger = configure_logging()
        assert isinstance(logger, logging.Logger)

    def test_logger_name_and_level(self):
        """
        Logger should be named 'BASIC' and set to INFO level.
        """
        # Create logger and assert logger name and level
        logger = configure_logging()
        assert logger.name == 'BASIC'
        assert logger.level == logging.INFO

    def test_logger_has_stream_handler_with_formatter(self):
        """
        Logger should have a StreamHandler with the correct formatter.
        """
        # Create logger
        logger = configure_logging()

        # Assert correct number of handlers created
        handlers = logger.handlers
        assert len(handlers) == 1

        # Assert handler type
        handler = handlers[0]
        assert isinstance(handler, logging.StreamHandler)

        # Assert logging format
        formatter = handler.formatter
        assert formatter._fmt == '%(asctime)s - %(message)s'

    def test_warnings_are_ignored(self):
        """
        Warnings should be suppressed after configure_logging is called.
        """
        # Assert that warnings are suppressed
        configure_logging()
        with warnings.catch_warnings(record=True) as w:
            warnings.warn("This is a test warning", UserWarning)
            assert len(w) == 0
