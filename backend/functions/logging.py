# Import python dependencies
import warnings
import logging

def configure_logging() -> logging.Logger:
    '''
    Configures and returns a logger instance.

    This function sets up a basic logger named 'BASIC' with an INFO level.
    It ignores warnings, formats log messages with timestamps, and outputs
    logs to the console via a stream handler.

    Returns:
        logging.Logger: Configured logger instance.
    '''
    # Ignore warnings
    warnings.filterwarnings("ignore")

    # Configure Logger
    logger = logging.getLogger('BASIC')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    return logger
