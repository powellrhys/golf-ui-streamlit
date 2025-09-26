# Import python dependencies
import warnings
import logging

# ANSI color codes
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"

class ColorFormatter(logging.Formatter):
    """
    Custom logging formatter to add ANSI colors based on log level.
    """
    COLORS = {
        logging.DEBUG: BLUE,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: MAGENTA,
    }

    def format(self, record):
        """
        Function to dictate log message format
        """
        color = self.COLORS.get(record.levelno, RESET)

        # Apply color to the log level name
        record.levelname = f"{color}{record.levelname}{RESET}"

        # Format the message
        message = super().format(record)

        return message


def configure_logging() -> logging.Logger:
    '''
    Configures and returns a logger instance.

    This function sets up a basic logger named 'BASIC' with an INFO level.
    It ignores warnings, formats log messages with timestamps and colors,
    and outputs logs to the console via a stream handler.

    Returns:
        logging.Logger: Configured logger instance.
    '''
    # Ignore warnings
    warnings.filterwarnings("ignore")

    # Configure Logger
    logger = logging.getLogger('BASIC')
    logger.setLevel(logging.INFO)

    # Create formatter with timestamp, levelname, and message
    formatter = ColorFormatter('%(asctime)s - %(levelname)s - %(message)s')

    # StreamHandler for console output
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(formatter)

    # Avoid duplicate handlers if configure_logging() is called multiple times
    if not logger.handlers:
        logger.addHandler(log_handler)

    return logger
